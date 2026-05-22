"""
Shared Gemini utility functions used across services.
"""
import re


def clean_gemini_json_response(raw_response: str) -> str:
    """
    Strip markdown wrappers from Gemini response.
    
    Even with response_mime_type=application/json, older calls or
    recommendation_service may not use it — this is a safety net.
    
    Args:
        raw_response: Raw text from Gemini API
    Returns:
        Clean JSON string ready for json.loads()
    """
    text = raw_response.strip()

    # Remove ```json ... ``` or ``` ... ``` wrappers
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    # Extract just the JSON object from first { to last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1:
        text = text[first_brace:last_brace + 1]

    return text.strip()