import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from gemini_service import gemini_service, GeminiServiceError

logger = logging.getLogger("edugenie.learning_path")
router = APIRouter(tags=["Learning Path"])

class LearningPathRequest(BaseModel):
    topic: str = Field(..., description="Subject or skill to build a roadmap for (e.g., 'SQL', 'Data Science')", min_length=2, max_length=200)
    current_level: Optional[str] = Field("Beginner", description="Learner's current proficiency level (e.g., Absolute Beginner, Intermediate)")

    @field_validator("topic")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Topic cannot be empty.")
        return trimmed

class StageDetail(BaseModel):
    stage_title: str
    focus_summary: str
    what_to_learn: List[str]
    suggested_resources: List[str]

class LearningPathResponse(BaseModel):
    topic: str
    current_level: Optional[str] = "Beginner"
    overview: str
    estimated_timeline: str
    recommended_order: List[str]
    beginner: StageDetail
    intermediate: StageDetail
    advanced: StageDetail
    practice_suggestions: List[str]
    projects_exercises: List[str]
    recommended_media: List[str] # Recommended videos, articles, books

LEARNING_PATH_SYSTEM_PROMPT = (
    "You are an elite academic curriculum designer and career mentor. You create logical, structured, "
    "and highly motivating learning roadmaps that take students from fundamentals to mastery. "
    "You provide clear progression stages, hands-on project milestones, and curated, top-tier learning resources."
)

@router.post("/learn/recommendations", response_model=LearningPathResponse)
async def generate_learning_path(request: LearningPathRequest):
    """
    POST /learn/recommendations
    Generates a personalized, structured learning roadmap from Beginner to Advanced,
    complete with topics, learning objectives, suggested resources, timeline, and projects.
    """
    topic = request.topic.strip()
    level = (request.current_level or "Beginner").strip()
    logger.info(f"Received learning path request for topic='{topic}', current_level='{level}'")

    prompt = f"""
Create a personalized learning roadmap for mastering: "{topic}".
The learner's current background/level is: {level}.

Organize the roadmap rigorously into three distinct stages: Beginner, Intermediate, and Advanced.
Include curated study topics, high-quality recommended resources (books, videos, docs),
hands-on projects, practice exercises, and an estimated timeline.

You MUST respond strictly with a valid JSON object matching this schema:
{{
  "topic": "{topic}",
  "current_level": "{level}",
  "overview": "A motivating 2-sentence summary of what mastering this topic unlocks",
  "estimated_timeline": "e.g., 8-12 weeks (5-7 hours/week)",
  "recommended_order": [
    "Phase 1: Foundations & Core Concepts",
    "Phase 2: Practical Application & Workflows",
    "Phase 3: Deep Dives, Edge Cases & Real Projects"
  ],
  "beginner": {{
    "stage_title": "Foundations & Core Essentials",
    "focus_summary": "Core concepts to understand first",
    "what_to_learn": [
      "Core topic 1",
      "Core topic 2",
      "Core topic 3"
    ],
    "suggested_resources": [
      "Resource 1 (e.g. Official Documentation)",
      "Resource 2 (e.g. Recommended introductory course or tutorial)"
    ]
  }},
  "intermediate": {{
    "stage_title": "Applied Skills & Practical Fluency",
    "focus_summary": "Real-world techniques and intermediate patterns",
    "what_to_learn": [
      "Intermediate topic 1",
      "Intermediate topic 2",
      "Intermediate topic 3"
    ],
    "suggested_resources": [
      "Resource 1 (e.g. Interactive exercises or intermediate book)",
      "Resource 2 (e.g. Practical video series)"
    ]
  }},
  "advanced": {{
    "stage_title": "Mastery, Optimization & Architecture",
    "focus_summary": "High-level performance, scalability, and internal mechanisms",
    "what_to_learn": [
      "Advanced topic 1",
      "Advanced topic 2",
      "Advanced topic 3"
    ],
    "suggested_resources": [
      "Resource 1 (e.g. In-depth book or research papers)",
      "Resource 2 (e.g. Architecture case studies)"
    ]
  }},
  "practice_suggestions": [
    "Practical daily habit or coding exercise 1",
    "Practical daily habit or coding exercise 2"
  ],
  "projects_exercises": [
    "Beginner project: ...",
    "Intermediate project: ...",
    "Capstone project: ..."
  ],
  "recommended_media": [
    "Book: ...",
    "Video/Channel: ...",
    "Interactive Site: ..."
  ]
}}
"""

    try:
        data = gemini_service.generate_json(
            prompt=prompt,
            system_instruction=LEARNING_PATH_SYSTEM_PROMPT,
            temperature=0.4
        )

        def make_stage(key: str, default_title: str) -> StageDetail:
            raw = data.get(key, {})
            return StageDetail(
                stage_title=raw.get("stage_title", default_title),
                focus_summary=raw.get("focus_summary", "Core subject matter focus"),
                what_to_learn=raw.get("what_to_learn", ["Core concepts"]),
                suggested_resources=raw.get("suggested_resources", ["Curated learning references"])
            )

        return LearningPathResponse(
            topic=data.get("topic", topic),
            current_level=data.get("current_level", level),
            overview=data.get("overview", f"Comprehensive learning roadmap for {topic}"),
            estimated_timeline=data.get("estimated_timeline", "6-10 weeks"),
            recommended_order=data.get("recommended_order", ["Beginner Foundations", "Intermediate Practice", "Advanced Mastery"]),
            beginner=make_stage("beginner", "Beginner Foundations"),
            intermediate=make_stage("intermediate", "Intermediate Fluency"),
            advanced=make_stage("advanced", "Advanced Mastery"),
            practice_suggestions=data.get("practice_suggestions", ["Engage in consistent hands-on exercises."]),
            projects_exercises=data.get("projects_exercises", ["Build a portfolio-grade project."]),
            recommended_media=data.get("recommended_media", ["Consult leading industry books and documentation."])
        )

    except GeminiServiceError as ge:
        logger.error(f"Gemini error in /learn/recommendations: {ge.message}")
        raise HTTPException(status_code=ge.status_code, detail=ge.message)
    except Exception as e:
        logger.error(f"Unexpected error in /learn/recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="EduGenie couldn't build your learning path right now. Please try again."
        )
