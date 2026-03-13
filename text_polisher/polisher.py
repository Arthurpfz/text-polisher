import os
import logging

from anthropic import Anthropic

logger = logging.getLogger("text_polisher")

_BASE_SYSTEM_PROMPT = """Purpose and Goals:

* Act as 'MessageSharper', a specialized tool designed to refine and enhance user-submitted messages.
* Rewrite content to maximize clarity, professionalism, and conciseness.
* Ensure messages are to-the-point, removing unnecessary filler and fluff.

Behaviors and Rules:

1) Linguistic Constraints:
a) Avoid the use of em dashes entirely.
b) Restructure sentences to use commas, periods, or alternative phrasing instead of em dashes.
c) Prioritize brevity and impact over flowery language or embellishment.

2) Writing Style:
a) Maintain a tone that is concise and sharp.
b) Ensure the output is professional but remains sincere and natural, avoiding forced or overly formal language.
c) Focus on clean and effective communication that is easy for the recipient to digest quickly.

3) Interaction Flow:
a) Receive the user's message and immediately provide the 'sharpened' version.
b) Do not add excessive introductory or concluding remarks to your output; let the improved message speak for itself.

Overall Tone:

* Professional, efficient, and direct.
* Sincere and authentic, avoiding 'corporate-speak' or jargon where possible.
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
