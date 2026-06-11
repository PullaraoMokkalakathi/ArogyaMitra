# ──────────────────────────────────────────────────────────────
# app/services/groq_service.py
# Groq AI Coach for ArogyaMitra
# ──────────────────────────────────────────────────────────────

import json
import urllib.request
import urllib.error
import logging

from app.config import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)


def generate_coach_response(
    messages: list[dict],
    user_context: dict
) -> str:
    """
    Generate AI coach response using Groq.
    """

    try:
        # ──────────────────────────────────────────
        # Check API key
        # ──────────────────────────────────────────
        if not settings.groq_api_key:
            return (
                "Groq API key missing. "
                "Please configure backend."
            )

        print(
            "GROQ KEY:",
            settings.groq_api_key[:15]
        )

        # ──────────────────────────────────────────
        # System Prompt
        # ──────────────────────────────────────────
        system_prompt = f"""
You are ArogyaMitra,
an elite AI fitness coach.

Be:
- Friendly
- Motivational
- Practical
- Short and useful

Focus ONLY on:
fitness, nutrition,
recovery and wellness.

Never give unsafe advice.

User Goal:
{user_context.get('goal', 'N/A')}

BMI:
{user_context.get('bmi', 'N/A')}

Activity Level:
{user_context.get('activity_level', 'N/A')}

Workout Streak:
{user_context.get('current_streak', 0)}

Total Workouts:
{user_context.get('total_workouts', 0)}
"""

        # ──────────────────────────────────────────
        # Latest User Message
        # ──────────────────────────────────────────
        latest_message = ""

        for msg in reversed(messages):
            if msg.get("role") == "user":
                latest_message = msg.get(
                    "content",
                    ""
                )
                break

        # ──────────────────────────────────────────
        # Request Payload
        # ──────────────────────────────────────────
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": latest_message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        headers = {
            "Authorization":
                f"Bearer {settings.groq_api_key}",
            "Content-Type":
                "application/json"
        }

        # ──────────────────────────────────────────
        # Send Request
        # ──────────────────────────────────────────
        req = urllib.request.Request(
            GROQ_API_URL,
            data=json.dumps(payload).encode(
                "utf-8"
            ),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(
            req,
            timeout=20
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        ai_response = (
            data["choices"][0]
            ["message"]["content"]
            .strip()
        )

        print("✅ GROQ SUCCESS")

        return ai_response

    # ──────────────────────────────────────────────
    # HTTP Errors
    # ──────────────────────────────────────────────
    except urllib.error.HTTPError as e:

        error = e.read().decode()

        print(
            "\n========== GROQ FULL ERROR =========="
        )
        print("STATUS:", e.code)
        print("ERROR:")
        print(error)
        print(
            "=====================================\n"
        )

        return (
            f"Groq Error {e.code}: "
            f"{error}"
        )

    # ──────────────────────────────────────────────
    # Network Errors
    # ──────────────────────────────────────────────
    except urllib.error.URLError as e:

        print("Network Error:", e)

        return (
            "Unable to connect to "
            "Groq servers."
        )

    # ──────────────────────────────────────────────
    # Unexpected Errors
    # ──────────────────────────────────────────────
    except Exception as e:

        print("Unexpected Error:", e)

        return (
            "Coach is warming up 💪 "
            "Try again in a moment."
        )