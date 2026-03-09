from pathlib import Path


class WhisperASR:
    def __init__(self, model_name: str, use_gpu: bool = False) -> None:
        self._model_name = model_name
        self._use_gpu = use_gpu
        self._model = None

    def _lazy_load(self) -> None:
        if self._model is not None:
            return
        import whisper

        self._model = whisper.load_model(self._model_name)

    def transcribe(self, audio_path: Path, source_language: str) -> dict[str, str]:
        self._lazy_load()
        result = self._model.transcribe(str(audio_path), language=source_language)
        return {
            "text": (result.get("text") or "").strip(),
        }
