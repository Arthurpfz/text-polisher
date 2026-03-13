import os
import logging

from anthropic import Anthropic

logger = logging.getLogger("text_polisher")

_TONE_INSTRUCTIONS = {
    "professional": "Make it clearer and more professional.",
    "friendly": "Make it warm, approachable, and clear.",
    "informal": "Keep it casual and natural. Fix only real errors.",
    "ironic": "Keep the ironic/sarcastic edge. Polish the delivery.",
}

_LANG_INSTRUCTIONS = {
    "english": "Reply in English.",
    "french": "Reply in French.",
    "german": "Reply in German.",
}


def _build_system_prompt(language: str, tone: str) -> str:
    tone_part = _TONE_INSTRUCTIONS.get(tone, _TONE_INSTRUCTIONS["professional"])
    lang_part = _LANG_INSTRUCTIONS.get(language, _LANG_INSTRUCTIONS["english"])
    return (
        f"Improve this message. Keep the intent and tone. Fix grammar. "
        f"{tone_part} {lang_part} "
        f"Reply with ONLY the improved text, nothing else."
    )


class Polisher:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Add it to your .env file or export it as an environment variable."
            )
        self._client = Anthropic(api_key=api_key)

    def polish(self, text: str, language: str = "english", tone: str = "professional") -> str:
        logger.info("API call started")
        response = self._client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=2048,
            system=_build_system_prompt(language, tone),
            messages=[{"role": "user", "content": text}],
        )
        logger.info("API call completed")
        return response.content[0].text
