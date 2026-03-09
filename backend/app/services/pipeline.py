from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from app.core.config import Settings
from app.services.components.asr import WhisperASR
from app.services.components.lipsync import MockLipSync, Wav2LipSync
from app.services.components.media import extract_audio_from_video
from app.services.components.translate import NLLBTranslator
from app.services.components.tts import CoquiTTSService, MockTTSService


class TranslationPipeline:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._mode = settings.pipeline_mode.strip().lower()

        if self._mode == "real":
            self._asr = WhisperASR(settings.whisper_model, use_gpu=settings.use_gpu)
            self._translator = NLLBTranslator(settings.nllb_model, use_gpu=settings.use_gpu)
            self._tts = CoquiTTSService(settings.coqui_model, use_gpu=settings.use_gpu)
            self._lipsync = Wav2LipSync(
                repo_path=settings.wav2lip_repo,
                checkpoint_path=settings.wav2lip_checkpoint,
                python_bin=settings.wav2lip_python_bin,
            )
        else:
            self._asr = None
            self._translator = None
            self._tts = MockTTSService()
            self._lipsync = MockLipSync()

    def run(
        self,
        job_id: str,
        source_video_path: Path,
        source_language: str,
        target_language: str,
        speaker_wav_path: Optional[Path],
        progress_cb,
    ) -> dict[str, str]:
        if self._mode != "real":
            return self._run_mock(job_id, source_video_path, target_language, progress_cb)

        job_tmp_dir = self._settings.tmp_dir / job_id
        job_tmp_dir.mkdir(parents=True, exist_ok=True)
        extracted_audio_path = job_tmp_dir / "source.wav"
        translated_speech_path = job_tmp_dir / "translated.wav"
        output_video_path = self._settings.outputs_dir / f"{job_id}.mp4"

        progress_cb(0.1)
        extract_audio_from_video(source_video_path, extracted_audio_path)

        progress_cb(0.35)
        transcription = self._asr.transcribe(extracted_audio_path, source_language)
        transcript_text = transcription["text"]
        if not transcript_text:
            raise ValueError("No speech detected in input video")

        progress_cb(0.55)
        translated_text = self._translator.translate(transcript_text, source_language, target_language)

        progress_cb(0.75)
        self._tts.synthesize(translated_text, translated_speech_path, target_language, speaker_wav=speaker_wav_path)

        progress_cb(0.9)
        self._lipsync.generate(source_video_path, translated_speech_path, output_video_path)

        progress_cb(1.0)
        return {
            "transcript": transcript_text,
            "translated_text": translated_text,
            "output_path": str(output_video_path),
        }

    def _run_mock(self, job_id: str, source_video_path: Path, target_language: str, progress_cb) -> dict[str, str]:
        output_video_path = self._settings.outputs_dir / f"{job_id}.mp4"
        progress_cb(0.3)

        translated_speech_path = self._settings.tmp_dir / job_id / "translated.wav"
        translated_speech_path.parent.mkdir(parents=True, exist_ok=True)
        transcript = "This is a mock transcription from the uploaded video."
        translated_text = f"[{target_language}] {transcript}"
        self._tts.synthesize(translated_text, translated_speech_path, target_language)

        progress_cb(0.7)
        self._lipsync.generate(source_video_path, translated_speech_path, output_video_path)

        progress_cb(1.0)
        return {
            "transcript": transcript,
            "translated_text": translated_text,
            "output_path": str(output_video_path),
        }
