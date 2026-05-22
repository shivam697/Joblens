"""
Resume Pydantic Schemas — Request/Response validation for resume endpoints
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    """
    Resume data returned to the frontend.
    Excludes parsed_text to keep responses lightweight —
    full text is only needed for ATS analysis, not for listing.
    """
    id: str
    file_name: str
    file_type: str
    is_active: bool
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDetailResponse(BaseModel):
    """
    Full resume data including parsed text.
    Used when displaying resume content or sending to ATS analysis.
    """
    id: str
    file_name: str
    file_type: str
    parsed_text: str
    is_active: bool
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
