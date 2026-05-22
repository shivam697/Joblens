"""
ATS Analysis Pydantic Schemas — Request/Response validation for both ATS flows
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class ATSQuickAnalyzeRequest(BaseModel):
    """
    Schema for Flow 1 — Quick ATS Check.
    User provides job description text and optionally selects an existing resume.
    If no resume_id, a file upload is expected (handled as multipart form data).
    """
    job_description: str
    resume_id: Optional[str] = None

    @field_validator("job_description")
    @classmethod
    def validate_job_description(cls, value: str) -> str:
        if len(value.strip()) < 50:
            raise ValueError(
                "Job description must be at least 50 characters for meaningful analysis"
            )
        return value.strip()


class ATSJobAnalyzeRequest(BaseModel):
    """
    Schema for Flow 2 — Job-Linked ATS Analysis.
    Only needs the job application ID — backend fetches resume and JD automatically.
    """
    job_application_id: str


class ATSStatusResponse(BaseModel):
    """
    ATS report status response — used for both polling and final result.
    When status is 'pending', report will be None.
    When status is 'completed', report contains the full analysis.
    """
    report_id: str
    status: str  # pending, completed, failed
    ats_source: str  # quick_check or job_linked
    overall_score: Optional[int] = None
    generated_at: datetime
    completed_at: Optional[datetime] = None
    report: Optional[dict] = None
    error_message: Optional[str] = None
    resume_text_snapshot: Optional[str] = None
    job_description_snapshot: Optional[str] = None
    job_application_id: Optional[str] = None
