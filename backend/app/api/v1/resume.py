"""
Resume API Routes — Upload, list, delete, and activate resumes

Supports PDF and plain text file uploads.
PDF parsing is done in a threadpool executor to never block the async event loop.
Each user gets their own subdirectory in the uploads folder.
"""

import asyncio
import logging
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.resume import Resume
from app.schemas.resume import ResumeResponse
from app.services.resume_service import parse_pdf_file, parse_text_file

logger = logging.getLogger(__name__)

router = APIRouter()

# Allowed MIME types for resume uploads
ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "text/plain": "text",
}


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a resume file (PDF or plain text).

    Steps:
    1. Validate file type (MIME type check, not just extension)
    2. Validate file size (max MAX_FILE_SIZE_MB)
    3. Save file to disk in user's subdirectory
    4. Parse file to extract text (threadpool for PDF)
    5. Save Resume record to MySQL
    """
    try:
        # Step 1: Validate MIME type — checking actual content type, not just extension
        # This prevents someone from renaming a .exe to .pdf
        content_type = file.content_type
        if content_type not in ALLOWED_MIME_TYPES:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Only PDF and text files are allowed.",
                    "data": None,
                },
            )

        file_type = ALLOWED_MIME_TYPES[content_type]

        # Step 2: Read file content and validate size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size_bytes:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit.",
                    "data": None,
                },
            )

        # Step 3: Save file to disk in user's subdirectory
        # Unique filename prevents collisions: {uuid}_{original_name}
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        user_upload_dir = os.path.join(settings.UPLOAD_DIR, current_user.id)
        os.makedirs(user_upload_dir, exist_ok=True)

        file_path = os.path.join(user_upload_dir, unique_filename)
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Step 4: Parse file to extract text
        # PDF parsing is SYNCHRONOUS — run in threadpool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        if file_type == "pdf":
            parsed_text = await loop.run_in_executor(None, parse_pdf_file, file_path)
        else:
            parsed_text = await loop.run_in_executor(None, parse_text_file, file_path)

        if not parsed_text or len(parsed_text.strip()) < 50:
            # Clean up file if parsing failed
            os.remove(file_path)
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Could not extract text from file. Please upload a valid resume.",
                    "data": None,
                },
            )

        # Step 5: Save Resume record to MySQL
        resume = Resume(
            user_id=current_user.id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file_type,
            parsed_text=parsed_text,
            is_active=False,
        )
        db.add(resume)
        await db.commit()
        await db.refresh(resume)

        resume_data = ResumeResponse.model_validate(resume).model_dump(mode="json")
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Resume uploaded successfully",
                "data": resume_data,
            },
        )

    except Exception as error:
        logger.error(f"Resume upload failed: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to upload resume. Please try again.",
                "data": None,
            },
        )


@router.get("/")
async def list_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all resumes for the current user, ordered by upload date (newest first).
    Includes is_active field so frontend can show which resume is currently active.
    """
    try:
        result = await db.execute(
            select(Resume)
            .where(Resume.user_id == current_user.id)
            .order_by(Resume.uploaded_at.desc())
        )
        resumes = result.scalars().all()
        resumes_data = [
            ResumeResponse.model_validate(r).model_dump(mode="json")
            for r in resumes
        ]

        return JSONResponse(
            content={
                "success": True,
                "message": "Resumes fetched",
                "data": resumes_data,
            }
        )

    except Exception as error:
        logger.error(f"Failed to list resumes: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to fetch resumes.",
                "data": None,
            },
        )


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a resume — removes file from disk and record from MySQL.
    Verifies the resume belongs to the current user before deleting.
    """
    try:
        # Find resume and verify ownership
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
                content={
                    "success": False,
                    "message": "Resume not found.",
                    "data": None,
                },
            )

        # Delete file from disk — handle case where file was already removed
        try:
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)
        except OSError as file_error:
            logger.warning(f"Could not delete file {resume.file_path}: {file_error}")

        # Delete database record
        await db.delete(resume)
        await db.commit()

        return JSONResponse(
            content={
                "success": True,
                "message": "Resume deleted successfully",
                "data": None,
            }
        )

    except Exception as error:
        logger.error(f"Failed to delete resume: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to delete resume.",
                "data": None,
            },
        )


@router.patch("/{resume_id}/activate")
async def activate_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Set a resume as the active resume.
    Only one resume per user can be active at a time.

    Steps:
    1. Deactivate ALL user's resumes in one query
    2. Activate the selected resume
    This ensures exactly one resume is active at any time.
    """
    try:
        # Verify resume exists and belongs to user
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
                content={
                    "success": False,
                    "message": "Resume not found.",
                    "data": None,
                },
            )

        # Step 1: Deactivate all user's resumes in one efficient query
        await db.execute(
            update(Resume)
            .where(Resume.user_id == current_user.id)
            .values(is_active=False)
        )

        # Step 2: Activate the selected resume
        resume.is_active = True
        await db.commit()
        await db.refresh(resume)

        resume_data = ResumeResponse.model_validate(resume).model_dump(mode="json")
        return JSONResponse(
            content={
                "success": True,
                "message": "Resume activated",
                "data": resume_data,
            }
        )

    except Exception as error:
        logger.error(f"Failed to activate resume: {error}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to activate resume.",
                "data": None,
            },
        )
