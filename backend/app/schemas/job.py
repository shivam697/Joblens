"""
Job Application Pydantic Schemas — Request/Response validation

These schemas enforce data integrity for all job application operations.
Platform and status values are validated against allowed enums.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# Valid platform values — must match database ENUM
VALID_PLATFORMS = (
    "naukri", "linkedin", "instahire", "foundit", "indeed",
    "glassdoor", "internshala", "wellfound", "other",
)

# Valid status values — represents full job application lifecycle
VALID_STATUSES = (
    "saved", "applied", "screening", "interview_scheduled",
    "interview_done", "offered", "rejected", "accepted", "withdrawn",
)

# Valid interview modes
VALID_INTERVIEW_MODES = ("online", "in_person", "phone")


class JobCreateSchema(BaseModel):
    """Schema for creating a new job application."""
    company_name: str
    platform: str
    job_link: Optional[str] = None
    job_description: Optional[str] = None
    hr_name: Optional[str] = None
    hr_contact: Optional[str] = None
    hr_email: Optional[str] = None
    status: str = "saved"
    interview_datetime: Optional[datetime] = None
    interview_mode: Optional[str] = None
    interview_platform: Optional[str] = None
    interview_link: Optional[str] = None
    interview_notes: Optional[str] = None
    salary_offered: Optional[float] = None
    notes: Optional[str] = None
    resume_id: Optional[str] = None

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, value: str) -> str:
        if not value or len(value.strip()) < 1:
            raise ValueError("Company name is required")
        return value.strip()

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, value: str) -> str:
        if value not in VALID_PLATFORMS:
            raise ValueError(f"Platform must be one of: {', '.join(VALID_PLATFORMS)}")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return value

    @field_validator("interview_mode")
    @classmethod
    def validate_interview_mode(cls, value: Optional[str]) -> Optional[str]:
        if value and value not in VALID_INTERVIEW_MODES:
            raise ValueError(f"Interview mode must be one of: {', '.join(VALID_INTERVIEW_MODES)}")
        return value


class JobUpdateSchema(BaseModel):
    """
    Schema for updating a job application.
    All fields are optional — only provided fields get updated.
    """
    company_name: Optional[str] = None
    platform: Optional[str] = None
    job_link: Optional[str] = None
    job_description: Optional[str] = None
    hr_name: Optional[str] = None
    hr_contact: Optional[str] = None
    hr_email: Optional[str] = None
    status: Optional[str] = None
    interview_datetime: Optional[datetime] = None
    interview_mode: Optional[str] = None
    interview_platform: Optional[str] = None
    interview_link: Optional[str] = None
    interview_notes: Optional[str] = None
    salary_offered: Optional[float] = None
    notes: Optional[str] = None
    resume_id: Optional[str] = None

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, value: Optional[str]) -> Optional[str]:
        if value and value not in VALID_PLATFORMS:
            raise ValueError(f"Platform must be one of: {', '.join(VALID_PLATFORMS)}")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value and value not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return value

    @field_validator("interview_mode")
    @classmethod
    def validate_interview_mode(cls, value: Optional[str]) -> Optional[str]:
        if value and value not in VALID_INTERVIEW_MODES:
            raise ValueError(f"Interview mode must be one of: {', '.join(VALID_INTERVIEW_MODES)}")
        return value


class JobResponse(BaseModel):
    """Full job application data returned to the frontend."""
    id: str
    company_name: str
    platform: str
    job_link: Optional[str] = None
    job_description: Optional[str] = None
    status: str
    interview_datetime: Optional[datetime] = None
    interview_mode: Optional[str] = None
    interview_platform: Optional[str] = None
    interview_link: Optional[str] = None
    interview_notes: Optional[str] = None
    hr_name: Optional[str] = None
    hr_contact: Optional[str] = None
    hr_email: Optional[str] = None
    salary_offered: Optional[float] = None
    notes: Optional[str] = None
    resume_id: Optional[str] = None
    ats_report_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    """Paginated list of job applications."""
    items: list[JobResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class JobStatsResponse(BaseModel):
    """Aggregated stats for the dashboard."""
    total: int
    by_status: dict[str, int]
    interviews_today: int
    interviews_today_list: list[JobResponse] = []
    by_platform: dict[str, int]
