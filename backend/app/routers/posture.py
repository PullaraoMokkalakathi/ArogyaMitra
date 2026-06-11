# ──────────────────────────────────────────────────────────────
# app/routers/posture.py
# Posture analysis endpoints — placeholder for MediaPipe integration.
# ──────────────────────────────────────────────────────────────

import logging

from fastapi import APIRouter, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posture", tags=["Posture Analysis"])


# ── Request Body Schema ──────────────────────────────────────────────

class PostureAnalyzeRequest(BaseModel):
    image: str


# ── POST /analyze ────────────────────────────────────────────────

@router.post(
    "/analyze",
    status_code=status.HTTP_200_OK,
    summary="Analyze posture from image frame",
    responses={
        422: {"description": "Invalid image data"},
    },
)
def analyze_posture(payload: PostureAnalyzeRequest) -> dict:
    """
    Analyze posture from a base64-encoded image frame.
    Returns mock feedback until MediaPipe integration is added.
    """
    feedbacks = [
        "Good posture",
        "Straighten your back",
        "Raise elbow higher",
        "Shoulders back",
        "Keep chin up",
    ]

    import random
    feedback = random.choice(feedbacks)
    score = random.randint(60, 95)

    logger.info(f"Posture analysis request received - returning mock feedback: {feedback}")

    return {
        "success": True,
        "feedback": feedback,
        "score": score,
    }