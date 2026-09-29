import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from gemini_service import gemini_service, GeminiServiceError

logger = logging.getLogger("edugenie.explain")
router = APIRouter(tags=["Explain"])

class ExplainRequest(BaseModel):
    concept: str = Field(..., description="The concept or topic to explain", min_length=2, max_length=500)
    level: Optional[str] = Field("beginner", description="Target learning level, e.g. beginner, intermediate, child")

    @field_validator("concept")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Concept cannot be empty or solely whitespace.")
        return trimmed

class ExplainResponse(BaseModel):
    concept: str
    simple_definition: str
    intuitive_explanation: str
    step_by_step: List[str]
    simple_example: str
    key_points: List[str]
    real_world_example: Optional[str] = None

EXPLAIN_SYSTEM_PROMPT = (
    "You are an inspiring educational teacher specialized in simplifying complex subjects for students. "
    "Your goal is to make any concept immediately graspable without heavy jargon, using intuitive analogies, "
    "relatable examples, and clear steps."
)

@router.post("/explain", response_model=ExplainResponse)
async def explain_concept(request: ExplainRequest):
    """
    POST /explain
    Explains a concept with beginner-friendly definitions, intuitive analogies,
    step-by-step breakdowns, simple examples, key points, and real-world applications.
    """
    concept = request.concept.strip()
    level = request.level.strip() if request.level else "beginner"
    logger.info(f"Received explain request: '{concept}' at level '{level}'")

    prompt = f"""
Explain the educational concept "{concept}" for a {level} student.
Avoid unnecessary academic jargon and make it enjoyable and crystal clear.

You MUST respond strictly with a valid JSON object matching this schema:
{{
  "concept": "{concept}",
  "simple_definition": "A 1-2 sentence ultra-clear definition in everyday language",
  "intuitive_explanation": "An intuitive, intuitive analogy or mental model explaining how it works",
  "step_by_step": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "simple_example": "A concrete, simple walkthrough or calculation demonstrating the concept",
  "key_points": [
    "Key formula, rule, or critical takeaway 1",
    "Key formula, rule, or critical takeaway 2"
  ],
  "real_world_example": "How this concept is used in everyday life, technology, nature, or industry"
}}
"""

    try:
        data = gemini_service.generate_json(
            prompt=prompt,
            system_instruction=EXPLAIN_SYSTEM_PROMPT,
            temperature=0.4
        )

        return ExplainResponse(
            concept=data.get("concept", concept),
            simple_definition=data.get("simple_definition", ""),
            intuitive_explanation=data.get("intuitive_explanation", ""),
            step_by_step=data.get("step_by_step", []),
            simple_example=data.get("simple_example", ""),
            key_points=data.get("key_points", []),
            real_world_example=data.get("real_world_example")
        )

    except GeminiServiceError as ge:
        logger.error(f"Gemini error in /explain: {ge.message}")
        raise HTTPException(status_code=ge.status_code, detail=ge.message)
    except Exception as e:
        logger.error(f"Unexpected error in /explain: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="EduGenie couldn't explain this concept right now. Please try again."
        )
