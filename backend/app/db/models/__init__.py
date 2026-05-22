# Database Models Package
# Import all models here so Alembic can detect them for auto-generation
from app.db.models.user import User
from app.db.models.resume import Resume
from app.db.models.job_application import JobApplication
from app.db.models.oauth_token import OAuthToken

__all__ = ["User", "Resume", "JobApplication", "OAuthToken"]
