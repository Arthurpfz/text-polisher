import logging

import numpy as np

logger = logging.getLogger("text_polisher")


class Transcriber:
    def __init__(self, model_name: str = "base"):
        self._model = None
        self._model_name = model_name

    def _ensure_loaded(self):
        if self._model is None:
            logger.info("Loading Whisper model '%s'...", self._model_name)
            import whisper
            self._model = whisper.load_model(self._model_name)
            logger.info("Whisper model loaded")

    def transcribe(self, audio: np.ndarray) -> str:
        if len(audio) == 0:
            return ""
        self._ensure_loaded()
        result = self._model.transcribe(audio, fp16=False)
        text = result["text"].strip()
        logger.info("Transcription complete (%d chars)", len(text))
        return text
