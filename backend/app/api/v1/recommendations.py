"""
Job Recommendations API — AI-powered role suggestions based on resume

Uses Gemini to analyze the user's active resume and suggest matching job roles.
Results are cached in MongoDB for 24 hours to minimize API costs.
"""

import logging

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_mongo_db, get_current_user
from app.db.models.user import User
from app.db.models.resume import Resume
from app.services.recommendation_service import (
    get_cached_recommendations,
    generate_recommendations,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def format_recommendation_doc(doc: dict) -> dict:
    """Convert MongoDB document to serializable dict."""
    return {
        "id": str(doc.get("_id", "")),
        "user_id": doc.get("user_id"),
        "resume_id": doc.get("resume_id"),
        "generated_at": doc.get("generated_at", "").isoformat() if doc.get("generated_at") else None,
        "candidate_level": doc.get("candidate_level"),
        "strongest_skills": doc.get("strongest_skills", []),
        "recommendations": doc.get("recommendations", []),
    }


@router.post("/")
async def create_recommendations(
    force: bool = Query(False, description="Bypass 24h cache and regenerate"),
    db: AsyncSession = Depends(get_db),
    mongo: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate job recommendations based on the user's active resume.

    Steps:
    1. Find user's active resume
    2. Check MongoDB cache (24-hour validity)
    3. If cached: return immediately (no Gemini call)
    4. If not cached: call Gemini, save result, return
    """
    try:
        # Step 1: Get user's active resume
        result = await db.execute(
            select(Resume).where(
                Resume.user_id == current_user.id,
                Resume.is_active == True,  # noqa: E712
            )
        )
        active_resume = result.scalar_one_or_none()

        if not active_resume:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Please upload and activate a resume first.",
                    "data": None,
                },
            )

        # Step 2: Check cache (skip when force=true for Regenerate button)
        cached = None
        if not force:
            cached = await get_cached_recommendations(
                mongo, current_user.id, active_resume.id
            )

        if cached:
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Recommendations fetched (cached)",
                    "data": format_recommendation_doc(cached),
                }
            )

        # Step 3: Generate new recommendations via Gemini
        doc = await generate_recommendations(
            mongo=mongo,
            user_id=current_user.id,
            resume_id=active_resume.id,
            resume_text=active_resume.parsed_text,
        )

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Recommendations generated",
                "data": format_recommendation_doc(doc),
            },
        )

    except ValueError as error:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": str(error),
                "data": None,
            },
        )
    except Exception as error:
        logger.error(f"Failed to generate recommendations: {error}")
        message = "Failed to generate recommendations. Please try again."
        if "GEMINI" in str(error).upper() or "API key" in str(error):
            message = "AI service is not configured. Please set GEMINI_API_KEY."
        elif "404" in str(error) and "model" in str(error).lower():
            message = "AI model unavailable. Check GEMINI_MODEL in server config."
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": message,
                "data": None,
            },
        )


@router.get("/")
async def get_recommendations(
    mongo: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the most recent recommendations for the current user.
    Returns empty state if no recommendations have been generated yet.
    """
    try:
        # Find most recent recommendation document
        doc = await mongo.job_recommendations.find_one(
            {"user_id": current_user.id},
            sort=[("generated_at", -1)],
        )

        if not doc:
            return JSONResponse(
                content={
                    "success": True,
                    "message": "No recommendations yet",
                    "data": None,
                }
            )

        return JSONResponse(
            content={
                "success": True,
                "message": "Recommendations fetched",
                "data": format_recommendation_doc(doc),
            }
        )

    except Exception as error:
        logger.error(f"Failed to get recommendations: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to fetch recommendations.",
                "data": None,
            },
        )
