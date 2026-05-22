"""
ATS Analysis Service — Gemini AI integration for resume analysis

JobLense supports two ATS analysis flows:

1. Quick Check (/ats/check): User uploads resume + pastes JD directly.
   Perfect for quickly testing a resume before applying. No job tracking needed.
   Great for freshers who want to optimize their resume for a job description
   they found online before even deciding to apply.

2. Job-Linked (/jobs/{id} page): ATS analysis tied to a specific tracked job.
   The report is permanently saved against that company and job application.
   User can always revisit which resume version they used and what score they got.
   Better for tracking and improving over time.

Interview talking point: "I built two flows because different users have
different needs. Some want a quick check before applying. Others want to
track ATS scores per company over time. Both use the same underlying
Gemini analysis — just different entry points and data linkage."

Key technical decisions:
- Gemini 2.5 Flash: latest and most capable model for structured output
- response_mime_type="application/json": forces Gemini to return pure JSON always
  This eliminates markdown wrapper issues and JSON parse failures completely
- run_in_executor: Gemini SDK is synchronous — we run it in a threadpool
  so it never blocks the async FastAPI event loop
- temperature=0.3: lower temperature = more consistent, predictable JSON structure
"""

import asyncio
import json
import logging
from datetime import datetime

import google.generativeai as genai
from bson import ObjectId

from app.core.config import settings
from app.db.mongodb import get_mongo_database

logger = logging.getLogger(__name__)

# Configure Gemini with our API key from .env
# This runs once when the module is imported
genai.configure(api_key=settings.GEMINI_API_KEY)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GEMINI ATS ANALYSIS PROMPT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ATS_ANALYSIS_PROMPT = """
You are an expert ATS (Applicant Tracking System) analyzer and professional career coach
with 15 years of experience helping candidates get shortlisted at top tech companies.

Carefully read the resume and job description below.
Give detailed, specific, and actionable feedback — not generic advice.
Reference actual content from the resume in your feedback.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return a valid JSON object with exactly this structure.

{{
  "overall_score": <integer 0 to 100 — honest score of how well this resume matches this JD>,
  "keyword_analysis": {{
    "matched_keywords": [<keywords appearing in both resume and JD — be thorough>],
    "missing_keywords": [<important keywords from JD not in resume — prioritize required skills>],
    "match_percentage": <integer 0-100>
  }},
  "skills_gap": {{
    "hard_skills_missing": [<specific technical skills in JD not found in resume>],
    "soft_skills_missing": [<soft skills mentioned in JD not demonstrated in resume>]
  }},
  "grammar_issues": [
    {{
      "original": "<exact phrase from resume that has an issue>",
      "suggestion": "<specific improved version with better language>",
      "reason": "<one sentence explaining why this is better>"
    }}
  ],
  "format_suggestions": [<specific format improvements — reference actual resume structure>],
  "quantification_suggestions": [<specific lines in resume where adding numbers would help>],
  "action_verb_suggestions": [
    {{
      "weak": "<weak phrase currently used in resume>",
      "strong": "<stronger more impactful replacement>"
    }}
  ],
  "section_feedback": {{
    "summary": "<specific feedback on summary section or note if it is missing>",
    "experience": "<specific feedback referencing actual experience entries>",
    "education": "<feedback on education section>",
    "skills": "<feedback on skills section and what to add or reorganize>",
    "projects": "<feedback on projects section or note if missing>"
  }},
  "tailoring_suggestions": [<specific ways to customize this resume for this exact job>],
  "top_5_recommendations": [
    "<most impactful change — be very specific>",
    "<second most impactful change>",
    "<third>",
    "<fourth>",
    "<fifth>"
  ]
}}
"""


def _call_gemini_sync(prompt: str) -> str:
    """
    Synchronous Gemini API call — runs in a threadpool executor.

    Why this is a plain sync function and not async:
    The google-generativeai SDK is synchronous. If we called it directly
    inside an async function, it would block the entire FastAPI event loop
    and freeze all other requests until Gemini responds (15-30 seconds).

    Instead we wrap it in run_in_executor() which runs it in a separate
    thread — the event loop stays free to handle other requests.

    Key config decisions:
    - model: gemini-2.5-flash — latest, fastest, best for structured output
    - temperature 0.3: lower = more consistent JSON structure, less creative variation
    - max_output_tokens 4096: enough for a detailed ATS report
    - response_mime_type application/json: THIS IS THE KEY FIX
      Forces Gemini to always return pure valid JSON — no markdown wrappers,
      no backticks, no "Here is the analysis:" prefix text.
      Eliminates JSON parse failures completely.

    Args:
        prompt: Full ATS analysis prompt with resume and JD inserted

    Returns:
        Raw response text from Gemini (guaranteed JSON due to mime type)

    Raises:
        ValueError: If Gemini returns empty response
        Exception: Any Gemini API error (rate limit, invalid key, etc.)
    """
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=8192,
            # Force pure JSON output — no markdown, no backticks, no extra text
            # This is the most reliable way to get clean JSON from Gemini
            response_mime_type="application/json",
        ),
    )

    response = model.generate_content(prompt)

    # Validate response is not empty
    if not response or not response.text:
        raise ValueError(
            "Gemini returned an empty response. "
            "This may be due to safety filters or API issues."
        )

    return response.text


async def run_ats_analysis(
    report_id: str,
    resume_text: str,
    job_description: str,
    user_id: str,
    job_application_id: str | None = None,
) -> None:
    """
    Background task that calls Gemini and saves the result to MongoDB.

    This function runs AFTER the HTTP response has been sent to the user.
    The user receives { status: 'pending', report_id } immediately.
    This function updates that MongoDB document when analysis is complete.

    Why background task and not just await:
    Gemini takes 15-30 seconds to analyze a resume. We cannot make the user
    wait that long for an HTTP response. So we return immediately with a
    report_id and run this analysis in the background. The frontend polls
    GET /ats/report/{report_id} every 3 seconds until status changes.

    Steps:
    1. Validate inputs are not empty
    2. Build prompt by inserting resume text and job description
    3. Call Gemini via run_in_executor (non-blocking threadpool)
    4. Parse the JSON response
    5. Save completed report to MongoDB
    6. On any error — mark report as failed so frontend can show error

    Args:
        report_id: MongoDB ObjectId string of the pending report document
        resume_text: Extracted text content from the resume file
        job_description: Job description text provided by the user
        user_id: Current user UUID — for ownership and logging
        job_application_id: Optional — only set for Flow 2 (job-linked analysis)
    """
    mongo_db = get_mongo_database()

    try:
        # ── Step 1: Validate inputs ──────────────────────────────────
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set in .env — "
                "get your key from https://aistudio.google.com/apikey"
            )

        if not resume_text or len(resume_text.strip()) < 10:
            raise ValueError("Resume text is too short to analyze")

        if not job_description or len(job_description.strip()) < 10:
            raise ValueError("Job description is too short to analyze")

        # ── Step 2: Build prompt ─────────────────────────────────────
        # Trim inputs to avoid token overflow
        # gemini-2.5-flash supports 1M tokens but we keep it reasonable
        trimmed_resume = resume_text.strip()[:8000]
        trimmed_jd = job_description.strip()[:4000]

        prompt = ATS_ANALYSIS_PROMPT.format(
            resume_text=trimmed_resume,
            job_description=trimmed_jd,
        )

        # ── Step 3: Call Gemini in threadpool ────────────────────────
        # run_in_executor runs the sync function in a separate thread
        # so the FastAPI event loop is never blocked during the API call
        logger.info(
            f"Starting Gemini ATS analysis — "
            f"report: {report_id} | user: {user_id}"
        )

        loop = asyncio.get_event_loop()
        raw_response = await loop.run_in_executor(
            None,               # None = use default ThreadPoolExecutor
            _call_gemini_sync,  # Sync function to run in thread
            prompt,             # Argument passed to the function
        )

        # Log first 300 chars of response for debugging
        logger.info(
            f"Gemini response received for report {report_id}: "
            f"{raw_response[:300]}"
        )

        # ── Step 4: Parse JSON response ──────────────────────────────
        # response_mime_type="application/json" guarantees clean JSON
        # but we still wrap in try/except as a safety net
        report_data = json.loads(raw_response)

        # Validate the most critical field exists
        if "overall_score" not in report_data:
            raise ValueError(
                f"Gemini response missing 'overall_score' field. "
                f"Got keys: {list(report_data.keys())}"
            )

        # Ensure score is a valid integer between 0 and 100
        overall_score = int(report_data.get("overall_score", 0))
        overall_score = max(0, min(100, overall_score))  # Clamp to 0-100

        # ── Step 5: Save completed report to MongoDB ─────────────────
        await mongo_db.ats_reports.update_one(
            {"_id": ObjectId(report_id)},
            {
                "$set": {
                    "status": "completed",
                    "overall_score": overall_score,
                    "report": report_data,
                    "completed_at": datetime.utcnow(),
                    "error_message": None,
                }
            },
        )

        logger.info(
            f"ATS analysis completed successfully — "
            f"report: {report_id} | score: {overall_score}/100"
        )

    except json.JSONDecodeError as parse_error:
        # Should rarely happen with response_mime_type=application/json
        # but handle it gracefully just in case
        error_message = "AI response format error. Please try again."
        logger.error(
            f"JSON parse failed for report {report_id}: {parse_error}"
        )

        await mongo_db.ats_reports.update_one(
            {"_id": ObjectId(report_id)},
            {
                "$set": {
                    "status": "failed",
                    "error_message": error_message,
                    "completed_at": datetime.utcnow(),
                }
            },
        )

    except Exception as error:
        # Handles: invalid API key, rate limit exceeded, network error,
        # empty response, missing fields, any other unexpected error
        error_message = str(error)[:300] if str(error) else "Analysis failed. Please try again."
        logger.error(
            f"ATS analysis failed for report {report_id}: {error}",
            exc_info=True,  # Logs full traceback for debugging
        )

        await mongo_db.ats_reports.update_one(
            {"_id": ObjectId(report_id)},
            {
                "$set": {
                    "status": "failed",
                    "error_message": error_message,
                    "completed_at": datetime.utcnow(),
                }
            },
        )