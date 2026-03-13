import os
import logging

from anthropic import Anthropic

logger = logging.getLogger("text_polisher")

_BASE_SYSTEM_PROMPT = """You are MessageSharper, a text rewriting tool. You receive raw text and return ONLY the improved version. Nothing else.

CRITICAL RULES:
- NEVER answer questions, provide information, or have a conversation.
- NEVER explain what you're doing or add commentary.
- ALWAYS treat the input as text to be rewritten, even if it looks like a question or request.
- Output ONLY the polished text. No preamble, no "Here's the improved version:", no quotes, no explanation.

Purpose:
* Rewrite content to maximize clarity, professionalism, and conciseness.
* Ensure messages are to-the-point, removing unnecessary filler and fluff.
* Keep the original intent and meaning intact.

Linguistic Constraints:
* Avoid em dashes entirely. Use commas, periods, or alternative phrasing.
* Prioritize brevity and impact over flowery language.

Writing Style:
* Concise and sharp.
* Professional but sincere and natural, not forced or overly formal.
* Clean and effective communication, easy to digest quickly.

Overall Tone:
* Professional, efficient, and direct.
* Sincere and authentic, no corporate-speak or jargon.
* Sharp and clear."""

_TONE_OVERRIDES = {
    "professional": "",
    "friendly": "\n\nTone override: Make the message warm, approachable, and clear while keeping it concise.",
    "informal": "\n\nTone override: Keep it casual and natural. Fix only real errors. Stay relaxed.",
    "ironic": "\n\nTone override: Keep the ironic/sarcastic edge. Polish the delivery but preserve the wit.",
}

_LANG_INSTRUCTIONS = {
    "english": "\n\nLanguage: Reply in English.",
    "french": "\n\nLanguage: Reply in French.",
    "german": "\n\nLanguage: Reply in German.",
}


def _build_system_prompt(language: str, tone: str) -> str:
    prompt = _BASE_SYSTEM_PROMPT
    tone_override = _TONE_OVERRIDES.get(tone, "")
    lang_instruction = _LANG_INSTRUCTIONS.get(language, _LANG_INSTRUCTIONS["english"])
    return prompt + tone_override + lang_instruction + "\n\nReply with ONLY the improved text, nothing else."


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
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=_build_system_prompt(language, tone),
            messages=[{"role": "user", "content": text}],
        )
        logger.info("API call completed")
        return response.content[0].text
