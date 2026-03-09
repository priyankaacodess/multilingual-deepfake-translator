from __future__ import annotations

import wave
from pathlib import Path
from typing import Optional

from app.utils.lang_map import get_language


class CoquiTTSService:
    def __init__(self, model_name: str, use_gpu: bool = False) -> None:
        self._model_name = model_name
        self._use_gpu = use_gpu
        self._tts = None

    def _lazy_load(self) -> None:
        if self._tts is not None:
            return
        from TTS.api import TTS

        self._tts = TTS(model_name=self._model_name, progress_bar=False, gpu=self._use_gpu)

    def synthesize(self, text: str, output_path: Path, target_language: str, speaker_wav: Optional[Path] = None) -> None:
        self._lazy_load()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        language = get_language(target_language).coqui_code
        kwargs: dict[str, object] = {
            "text": text,
            "file_path": str(output_path),
            "language": language,
        }
        if speaker_wav:
            kwargs["speaker_wav"] = str(speaker_wav)
        self._tts.tts_to_file(**kwargs)


class MockTTSService:
    def synthesize(self, text: str, output_path: Path, target_language: str, speaker_wav: Optional[Path] = None) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        duration_seconds = 2
        sample_rate = 16000
        nframes = duration_seconds * sample_rate

        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b"\x00\x00" * nframes)
