"""
Recommendation Service — Gemini AI-powered job role suggestions

Analyzes the user's resume and suggests 8 best-fit job roles with
match percentages, salary ranges, and platform-specific search keywords.
Results are cached in MongoDB for 24 hours to avoid unnecessary API calls.
"""

import json
import logging
from datetime import datetime, timedelta

import google.generativeai as genai
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.services.gemini_utils import clean_gemini_json_response

logger = logging.getLogger(__name__)

# Configure Gemini (may already be configured in ats_service, but safe to call again)
genai.configure(api_key=settings.GEMINI_API_KEY)


RECOMMENDATION_PROMPT = """
You are an expert career counselor specializing in the Indian tech job market
with deep knowledge of placement trends for freshers and junior developers.

Analyze the resume below and recommend 8 job roles perfectly suited for this candidate.
Be realistic — base recommendations on their actual skills and experience level.
Do not recommend roles they are clearly unqualified for.

RESUME:
{resume_text}

Return ONLY a valid JSON object. No markdown. No backticks. Pure JSON only.

{{
  "candidate_level": "fresher OR junior OR mid-level OR senior",
  "strongest_skills": [<top 5 skills clearly demonstrated in resume>],
  "recommendations": [
    {{
      "job_title": "<specific job title as it appears on job boards>",
      "match_percentage": <integer 0-100 based on resume fit>,
      "why_it_fits": "<2-3 sentences referencing actual resume content>",
      "skills_you_have": [<skills from resume relevant to this role>],
      "skills_to_learn": [<3-4 specific skills to add for this role>],
      "salary_range_india": "<realistic range e.g. 4-8 LPA for freshers>",
      "platforms_to_search": ["LinkedIn", "Naukri", "Foundit"],
      "search_keywords": [<3-4 search terms to use on job platforms>]
    }}
  ]
}}
"""


async def get_cached_recommendations(
    mongo: AsyncIOMotorDatabase,
    user_id: str,
    resume_id: str,
) -> dict | None:
    """
    Check MongoDB for existing recommendations for this resume within last 24 hours.
    Returns cached result if found, None if cache miss.

    This is simple caching — avoids unnecessary Gemini API calls when the user
    hasn't changed their resume. Recommendations based on the same resume
    won't change significantly within a day.

    Args:
        mongo: MongoDB database instance
        user_id: Current user's UUID
        resume_id: Active resume UUID

    Returns:
        Cached recommendation document or None
    """
    cache_cutoff = datetime.utcnow() - timedelta(hours=24)

    cached = await mongo.job_recommendations.find_one(
        {
            "user_id": user_id,
            "resume_id": resume_id,
            "generated_at": {"$gte": cache_cutoff},
        },
        sort=[("generated_at", -1)],
    )

    return cached


async def generate_recommendations(
    mongo: AsyncIOMotorDatabase,
    user_id: str,
    resume_id: str,
    resume_text: str,
) -> dict:
    """
    Generate job recommendations using Gemini AI and save to MongoDB.

    Args:
        mongo: MongoDB database instance
        user_id: Current user's UUID
        resume_id: Active resume UUID
        resume_text: Extracted text from active resume

    Returns:
        Recommendation document with roles, skills, and search keywords

    Raises:
        Exception: If Gemini API call or JSON parsing fails
    """
    # Build prompt with resume text
    prompt = RECOMMENDATION_PROMPT.format(resume_text=resume_text)

    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")

    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    response = model.generate_content(prompt)

    # Clean and parse response
    clean_json = clean_gemini_json_response(response.text)
    recommendations_data = json.loads(clean_json)

    # Save to MongoDB for caching
    doc = {
        "user_id": user_id,
        "resume_id": resume_id,
        "generated_at": datetime.utcnow(),
        "candidate_level": recommendations_data.get("candidate_level", "fresher"),
        "strongest_skills": recommendations_data.get("strongest_skills", []),
        "recommendations": recommendations_data.get("recommendations", []),
    }
    result = await mongo.job_recommendations.insert_one(doc)
    doc["_id"] = result.inserted_id

    return doc
