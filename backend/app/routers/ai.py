from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.groq_service import (
    generate_coach_response
)

router = APIRouter(
    prefix="/ai",
    tags=["AI Coach"]
)


class MessageFormat(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[MessageFormat]


class ChatResponse(BaseModel):
    response: str


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat_with_coach(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Temporary version without JWT auth
    for testing AI coach.
    """

    # Dummy user data
    user_context = {
        "bmi": 20,
        "goal": "muscle gain",
        "activity_level": "moderate",
        "current_streak": 5,
        "best_posture_score": 92,
        "total_workouts": 15
    }

    msgs_dict = [
        {
            "role": m.role,
            "content": m.content
        }
        for m in request.messages
    ]

    response_text = (
        generate_coach_response(
            msgs_dict,
            user_context
        )
    )

    return ChatResponse(
        response=response_text
    )