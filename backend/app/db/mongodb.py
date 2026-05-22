"""
MongoDB Connection — Motor Async Client for MongoDB Atlas

We use MongoDB for AI-generated reports because they are large nested JSON
documents with no fixed schema. MySQL would require many joined tables for
this. MongoDB stores it naturally as one document and retrieves it in one query.

Interview talking point:
"I chose MySQL for structured data because it enforces schema and relationships
between users, resumes, and job applications. I chose MongoDB for AI-generated
reports because they are deeply nested JSON documents with no predictable schema
— MongoDB handles this naturally without requiring schema migrations every time
the AI prompt changes."
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


# Motor manages its own connection pool internally
# We create one client instance and reuse it across the entire application
mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGODB_URI)

# Get reference to our specific database
mongo_db: AsyncIOMotorDatabase = mongo_client[settings.MONGODB_DATABASE]


def get_mongo_database() -> AsyncIOMotorDatabase:
    """
    Returns the MongoDB database instance.
    Motor handles connection pooling automatically — no manual session management needed.
    """
    return mongo_db


async def create_mongodb_indexes() -> None:
    """
    Create performance indexes on MongoDB collections.
    Called once during FastAPI startup.

    Indexes ensure fast queries when:
    - Listing a user's ATS reports sorted by date
    - Looking up ATS report linked to a specific job application
    - Finding cached recommendations for a specific resume
    """
    # ATS reports — fast lookup by user and date (most common query)
    await mongo_db.ats_reports.create_index(
        [("user_id", 1), ("generated_at", -1)],
        name="idx_user_reports_by_date"
    )

    # ATS reports — fast lookup by job application (job-linked flow)
    await mongo_db.ats_reports.create_index(
        [("job_application_id", 1)],
        name="idx_report_by_job"
    )

    # Job recommendations — cache lookup by user + resume + date
    await mongo_db.job_recommendations.create_index(
        [("user_id", 1), ("resume_id", 1), ("generated_at", -1)],
        name="idx_recommendations_cache"
    )

    # OAuth tokens — fast lookup by user + provider
    await mongo_db.oauth_tokens.create_index(
        [("user_id", 1), ("provider", 1)],
        name="idx_oauth_tokens_user_provider",
        unique=True,
    )
