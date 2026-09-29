import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from gemini_service import gemini_service, GeminiServiceError

logger = logging.getLogger("edugenie.quiz")
router = APIRouter(tags=["Quiz"])

class QuizRequest(BaseModel):
    topic_or_passage: str = Field(..., description="A topic name or educational passage to generate a quiz from", min_length=2, max_length=5000)

    @field_validator("topic_or_passage")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Input topic or passage cannot be empty.")
        return trimmed

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class QuizResponse(BaseModel):
    topic_or_passage: str
    questions: List[QuizQuestion]

QUIZ_SYSTEM_PROMPT = (
    "You are an expert educational assessment creator. You generate thoughtful, high-quality, "
    "fair multiple-choice quiz questions that assess comprehension rather than mere rote memorization. "
    "Ensure each question has exactly 4 plausible options, with only one correct answer, and an insightful explanation."
)

@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """
    POST /quiz
    Generates exactly 3 multiple choice questions from a topic or passage.
    Returns validated strict JSON with 4 options per question, correct answer, and explanation.
    """
    input_text = request.topic_or_passage.strip()
    logger.info(f"Received quiz generation request for topic/passage: '{input_text[:60]}...'")

    prompt = f"""
Generate an educational quiz based on the following topic or text:
"{input_text}"

Requirements:
1. Generate EXACTLY 3 multiple-choice questions.
2. Each question MUST have EXACTLY 4 distinct answer options.
3. Specify the exact string of the correct answer (matching one of the 4 options verbatim).
4. Provide a clear, educational 1-2 sentence explanation of why that answer is correct and why it matters.

You MUST respond strictly with a valid JSON object following this exact schema:
{{
  "questions": [
    {{
      "question": "Clear and engaging question prompt 1",
      "options": [
        "Option A text",
        "Option B text",
        "Option C text",
        "Option D text"
      ],
      "correct_answer": "Option A text",
      "explanation": "Clear explanation of why this answer is correct."
    }},
    {{
      "question": "Question prompt 2",
      "options": [
        "Option A text",
        "Option B text",
        "Option C text",
        "Option D text"
      ],
      "correct_answer": "Option B text",
      "explanation": "Clear explanation."
    }},
    {{
      "question": "Question prompt 3",
      "options": [
        "Option A text",
        "Option B text",
        "Option C text",
        "Option D text"
      ],
      "correct_answer": "Option C text",
      "explanation": "Clear explanation."
    }}
  ]
}}
"""

    try:
        data = gemini_service.generate_json(
            prompt=prompt,
            system_instruction=QUIZ_SYSTEM_PROMPT,
            temperature=0.3
        )

        raw_questions = data.get("questions", [])
        if not isinstance(raw_questions, list) or len(raw_questions) == 0:
            raise GeminiServiceError("Model did not return a valid list of questions.", status_code=500)

        # Validate and format each question
        parsed_questions: List[QuizQuestion] = []
        for idx, q_dict in enumerate(raw_questions[:3]):
            q_text = str(q_dict.get("question", "")).strip()
            options = [str(opt).strip() for opt in q_dict.get("options", []) if str(opt).strip()]
            correct = str(q_dict.get("correct_answer", "")).strip()
            explanation = str(q_dict.get("explanation", "")).strip()

            # Ensure 4 options
            while len(options) < 4:
                options.append(f"Option {len(options)+1}")
            options = options[:4]

            # If correct_answer isn't exactly in options, normalize or match
            if correct not in options and len(options) > 0:
                # Check for prefix match like "A) Option text"
                found = False
                for opt in options:
                    if correct.lower() in opt.lower() or opt.lower() in correct.lower():
                        correct = opt
                        found = True
                        break
                if not found:
                    correct = options[0]

            parsed_questions.append(
                QuizQuestion(
                    question=q_text or f"Question {idx + 1}",
                    options=options,
                    correct_answer=correct,
                    explanation=explanation or "The correct option is the accurate answer to this educational problem."
                )
            )

        if len(parsed_questions) < 3:
            raise GeminiServiceError("Could not generate the required 3 quiz questions. Please try again.")

        return QuizResponse(
            topic_or_passage=input_text,
            questions=parsed_questions[:3]
        )

    except GeminiServiceError as ge:
        logger.error(f"Gemini error in /quiz: {ge.message}")
        raise HTTPException(status_code=ge.status_code, detail=ge.message)
    except Exception as e:
        logger.error(f"Unexpected error in /quiz: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="EduGenie couldn't generate the quiz right now. Please try again."
        )
