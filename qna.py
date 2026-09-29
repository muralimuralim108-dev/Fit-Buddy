import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from gemini_service import gemini_service, GeminiServiceError

logger = logging.getLogger("edugenie.qna")
router = APIRouter(tags=["Q&A"])

class QARequest(BaseModel):
    question: str = Field(..., description="The academic or educational question to answer", min_length=2, max_length=2000)

    @field_validator("question")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Question cannot be empty or solely whitespace.")
        return trimmed

class QAResponse(BaseModel):
    question: str
    answer: str
    confidence_note: Optional[str] = None

SYSTEM_INSTRUCTION_QA = (
    "You are EduGenie, an expert, encouraging, and highly knowledgeable educational AI tutor. "
    "Your mission is to help students learn and comprehend topics clearly.\n"
    "Guidelines:\n"
    "1. Answer the question directly and accurately.\n"
    "2. Explain the reasoning, underlying principles, or context when helpful for learning.\n"
    "3. Use student-friendly, engaging, and clear language.\n"
    "4. Avoid unnecessary fluff or overwhelming verbosity.\n"
    "5. If the question is ambiguous or underspecified, provide the most likely answer and politely ask for clarification on alternative interpretations.\n"
    "6. Never fabricate facts. If there is genuine scientific or historical debate or uncertainty, clearly state it."
)

@router.post("/qa", response_model=QAResponse)
async def ask_question(request: QARequest):
    """
    POST /qa
    Answers an educational or academic question directly, with reasoning and student-friendly explanations.
    """
    question = request.question.strip()
    logger.info(f"Received Q&A request: '{question[:50]}...'")

    prompt = f"Student Question: {question}\n\nPlease provide an educational, clear, and student-friendly answer."

    try:
        answer = gemini_service.generate_text(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_QA,
            temperature=0.5
        )
        return QAResponse(
            question=question,
            answer=answer
        )
    except GeminiServiceError as ge:
        logger.error(f"Gemini error in /qa: {ge.message}")
        raise HTTPException(status_code=ge.status_code, detail=ge.message)
    except Exception as e:
        logger.error(f"Unexpected error in /qa: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="EduGenie couldn't answer your question right now. Please try again."
        )
