import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from gemini_service import gemini_service, GeminiServiceError

logger = logging.getLogger("edugenie.summary")
router = APIRouter(tags=["Summarize"])

class SummarizeRequest(BaseModel):
    text: str = Field(..., description="The educational passage or article text to summarize", min_length=20, max_length=15000)

    @field_validator("text")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Text cannot be empty.")
        if len(trimmed.split()) < 5:
            raise ValueError("Please provide at least a few sentences to summarize.")
        return trimmed

class SummarizeResponse(BaseModel):
    summary: str
    key_points: List[str]
    original_word_count: int
    summary_word_count: int
    compression_ratio_pct: int

SUMMARY_SYSTEM_PROMPT = (
    "You are an expert educational research editor. Your role is to produce high-retention, concise, "
    "accurate summaries of educational texts. You strictly preserve the original core meaning, eliminate "
    "redundancies, and extract clear, memorable takeaways without hallucinating or introducing outside assumptions."
)

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """
    POST /summarize
    Condenses educational content into an accessible summary with high-impact key points.
    Preserves facts and removes fluff without altering the original meaning.
    """
    original_text = request.text.strip()
    words = original_text.split()
    original_word_count = len(words)
    logger.info(f"Received summarize request: {original_word_count} words")

    prompt = f"""
Summarize the following educational text for quick revision:
\"\"\"{original_text}\"\"\"

Instructions:
1. Preserve all critical factual information and underlying concepts.
2. Remove fluff, filler, and repetitive prose.
3. Write a concise, coherent summary paragraph (approx. 20-35% of the original length).
4. Extract 3 to 6 high-value, distinct bullet points highlighting key concepts or facts.
5. Strictly avoid adding external information not present in the source text.

You MUST respond strictly with a valid JSON object following this schema:
{{
  "summary": "Cohesive, clear summary paragraph here...",
  "key_points": [
    "Key takeaway point 1",
    "Key takeaway point 2",
    "Key takeaway point 3"
  ]
}}
"""

    try:
        data = gemini_service.generate_json(
            prompt=prompt,
            system_instruction=SUMMARY_SYSTEM_PROMPT,
            temperature=0.3
        )

        summary_text = data.get("summary", "").strip()
        key_points = [str(pt).strip() for pt in data.get("key_points", []) if str(pt).strip()]

        summary_word_count = len(summary_text.split())
        ratio = round((1 - (summary_word_count / max(1, original_word_count))) * 100)
        compression_ratio = max(0, min(95, ratio))

        return SummarizeResponse(
            summary=summary_text,
            key_points=key_points,
            original_word_count=original_word_count,
            summary_word_count=summary_word_count,
            compression_ratio_pct=compression_ratio
        )

    except GeminiServiceError as ge:
        logger.error(f"Gemini error in /summarize: {ge.message}")
        raise HTTPException(status_code=ge.status_code, detail=ge.message)
    except Exception as e:
        logger.error(f"Unexpected error in /summarize: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="EduGenie couldn't summarize this text right now. Please try again."
        )
