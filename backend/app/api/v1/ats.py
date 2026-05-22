"""
ATS Analysis API Routes — Quick Check (Flow 1) and Job-Linked (Flow 2)

JobLense supports two ATS analysis flows:

1. Quick Check (/ats/quick-analyze): User uploads resume + pastes JD directly.
   Perfect for quickly testing a resume before applying. No job tracking needed.
   Great for freshers who want to optimize their resume for a job description
   they found online before even deciding to apply.

2. Job-Linked (/ats/analyze): ATS analysis tied to a specific tracked job.
   The report is permanently saved against that company and job application.
   User can always revisit which resume version they used and what score they got.
   Better for tracking and improving over time.

Interview talking point: "I built two flows because different users have
different needs. Some want a quick check before applying. Others want to
track ATS scores per company over time. Both use the same underlying
Gemini analysis — just different entry points and data linkage."
"""

import asyncio
import logging
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db, get_mongo_db, get_current_user
from app.db.models.user import User
from app.db.models.resume import Resume
from app.db.models.job_application import JobApplication
from app.services.ats_service import run_ats_analysis
from app.services.resume_service import parse_pdf_file, parse_text_file

logger = logging.getLogger(__name__)

router = APIRouter()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FLOW 1 — QUICK ATS CHECK (Direct Upload)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.post("/quick-analyze")
async def quick_ats_analyze(
    background_tasks: BackgroundTasks,
    job_description: str = Form(...),
    resume_id: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    mongo: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    """
    Flow 1 — Quick ATS Check: Upload resume + paste JD → instant analysis.

    This flow is for users who want a quick ATS score without creating a job application.
    No job tracking needed — perfect for trying out different resume versions.

    Accepts either a file upload OR an existing resume_id — not both required.
    """
    try:
        resume_text = None

        # Option A: User selected an existing saved resume
        if resume_id:
            result = await db.execute(
                select(Resume).where(
                    Resume.id == resume_id,
                    Resume.user_id == current_user.id,
                )
            )
            resume = result.scalar_one_or_none()
            if not resume:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "message": "Resume not found.", "data": None},
                )
            resume_text = resume.parsed_text

        # Option B: User uploaded a new file
        elif file:
            filename = (file.filename or "").lower()
            content_type = file.content_type or ""
            is_pdf = (
                content_type == "application/pdf"
                or filename.endswith(".pdf")
                or (
                    content_type == "application/octet-stream"
                    and filename.endswith(".pdf")
                )
            )
            is_text = content_type == "text/plain" or filename.endswith(".txt")

            if not is_pdf and not is_text:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": "Only PDF and text files allowed.", "data": None},
                )

            # Read file content
            file_content = await file.read()
            if len(file_content) > settings.max_file_size_bytes:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit.", "data": None},
                )

            # Save temporarily and parse
            import tempfile
            import os

            suffix = ".pdf" if is_pdf else ".txt"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name

            try:
                loop = asyncio.get_event_loop()
                if is_pdf:
                    resume_text = await loop.run_in_executor(None, parse_pdf_file, tmp_path)
                else:
                    resume_text = await loop.run_in_executor(None, parse_text_file, tmp_path)
            finally:
                os.unlink(tmp_path)  # Clean up temp file

        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Please upload a resume or select an existing one.", "data": None},
            )

        # Validate we got meaningful text
        if not resume_text or len(resume_text.strip()) < 50:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Could not extract enough text from resume.", "data": None},
            )

        # Validate job description length
        if len(job_description.strip()) < 50:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Job description must be at least 50 characters.", "data": None},
            )

        # Create pending ATS report in MongoDB
        report_doc = {
            "user_id": current_user.id,
            "ats_source": "quick_check",
            "job_application_id": None,
            "resume_id": resume_id,
            "resume_text_snapshot": resume_text,
            "job_description_snapshot": job_description.strip(),
            "status": "pending",
            "error_message": None,
            "generated_at": datetime.utcnow(),
            "completed_at": None,
            "overall_score": None,
            "report": None,
        }
        result = await mongo.ats_reports.insert_one(report_doc)
        report_id = str(result.inserted_id)

        # Start Gemini analysis in background — response returns immediately
        background_tasks.add_task(
            run_ats_analysis,
            report_id=report_id,
            resume_text=resume_text,
            job_description=job_description.strip(),
            user_id=current_user.id,
        )

        return JSONResponse(
            status_code=202,
            content={
                "success": True,
                "message": "Analysis started",
                "data": {"report_id": report_id, "status": "pending"},
            },
        )

    except Exception as error:
        logger.error(f"Quick ATS analyze failed: {error}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Failed to start analysis.", "data": None},
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FLOW 2 — JOB-LINKED ATS ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.post("/analyze")
async def job_linked_ats_analyze(
    background_tasks: BackgroundTasks,
    job_application_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
    mongo: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    """
    Flow 2 — Job-Linked ATS Analysis: Analyze resume against a tracked job.

    The ATS report is permanently linked to the job application.
    Backend fetches resume text and job description from MySQL automatically.
    """
    try:
        # Fetch job application and verify ownership
        result = await db.execute(
            select(JobApplication).where(
                JobApplication.id == job_application_id,
                JobApplication.user_id == current_user.id,
                JobApplication.is_deleted == False,  # noqa: E712
            )
        )
        job = result.scalar_one_or_none()

        if not job:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "Job application not found.", "data": None},
            )

        # Verify job has a job description (needed for analysis)
        if not job.job_description or len(job.job_description.strip()) < 50:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Add a job description (min 50 chars) to enable ATS analysis.", "data": None},
            )

        # Verify job has a linked resume
        if not job.resume_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Link a resume to this job application first.", "data": None},
            )

        # Fetch the linked resume
        resume_result = await db.execute(
            select(Resume).where(Resume.id == job.resume_id)
        )
        resume = resume_result.scalar_one_or_none()

        if not resume:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Linked resume not found. It may have been deleted.", "data": None},
            )

        # Create pending ATS report in MongoDB
        report_doc = {
            "user_id": current_user.id,
            "ats_source": "job_linked",
            "job_application_id": job_application_id,
            "resume_id": job.resume_id,
            "resume_text_snapshot": resume.parsed_text,
            "job_description_snapshot": job.job_description,
            "status": "pending",
            "error_message": None,
            "generated_at": datetime.utcnow(),
            "completed_at": None,
            "overall_score": None,
            "report": None,
        }
        result = await mongo.ats_reports.insert_one(report_doc)
        report_id = str(result.inserted_id)

        # Save report ID to the job application in MySQL
        job.ats_report_id = report_id
        await db.commit()

        # Start Gemini analysis in background
        background_tasks.add_task(
            run_ats_analysis,
            report_id=report_id,
            resume_text=resume.parsed_text,
            job_description=job.job_description,
            user_id=current_user.id,
            job_application_id=job_application_id,
        )

        return JSONResponse(
            status_code=202,
            content={
                "success": True,
                "message": "Analysis started",
                "data": {"report_id": report_id, "status": "pending"},
            },
        )

    except Exception as error:
        logger.error(f"Job-linked ATS analyze failed: {error}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Failed to start analysis.", "data": None},
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REPORT POLLING AND HISTORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.get("/report/{report_id}")
async def get_ats_report(
    report_id: str,
    mongo: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get ATS report by ID — used for polling during analysis.

    Frontend polls this every 3 seconds until status becomes 'completed' or 'failed'.
    Verifies report belongs to current user before returning.
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(report_id):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Invalid report ID.", "data": None},
            )

        # Fetch report from MongoDB
        report = await mongo.ats_reports.find_one({"_id": ObjectId(report_id)})

        if not report:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "Report not found.", "data": None},
            )

        # Verify ownership — never show reports from other users
        if report.get("user_id") != current_user.id:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "Access denied.", "data": None},
            )

        # Convert MongoDB document to serializable dict
        report_data = {
            "report_id": str(report["_id"]),
            "status": report.get("status"),
            "ats_source": report.get("ats_source"),
            "overall_score": report.get("overall_score"),
            "generated_at": report.get("generated_at", "").isoformat() if report.get("generated_at") else None,
            "completed_at": report.get("completed_at", "").isoformat() if report.get("completed_at") else None,
            "report": report.get("report"),
            "error_message": report.get("error_message"),
            "job_application_id": report.get("job_application_id"),
            "resume_id": report.get("resume_id"),
        }

        return JSONResponse(
            content={
                "success": True,
                "message": "Report fetched",
                "data": report_data,
            }
        )

    except Exception as error:
        logger.error(f"Failed to get ATS report: {error}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Failed to fetch report.", "data": None},
        )


@router.get("/history")
async def get_ats_history(
    mongo: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all ATS reports for the current user, sorted by date (newest first).
    Returns summary view — score, source, date, status (not full report).
    """
    try:
        cursor = mongo.ats_reports.find(
            {"user_id": current_user.id},
            {
                # Project only summary fields for listing
                "status": 1,
                "ats_source": 1,
                "overall_score": 1,
                "generated_at": 1,
                "completed_at": 1,
                "job_application_id": 1,
                "error_message": 1,
            },
        ).sort("generated_at", -1).limit(50)

        reports = []
        async for doc in cursor:
            reports.append({
                "report_id": str(doc["_id"]),
                "status": doc.get("status"),
                "ats_source": doc.get("ats_source"),
                "overall_score": doc.get("overall_score"),
                "generated_at": doc.get("generated_at", "").isoformat() if doc.get("generated_at") else None,
                "completed_at": doc.get("completed_at", "").isoformat() if doc.get("completed_at") else None,
                "job_application_id": doc.get("job_application_id"),
            })

        return JSONResponse(
            content={
                "success": True,
                "message": "History fetched",
                "data": reports,
            }
        )

    except Exception as error:
        logger.error(f"Failed to get ATS history: {error}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Failed to fetch history.", "data": None},
        )
