from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.core.config import Settings
from app.models.schemas import JobStatus
from app.services.pipeline import TranslationPipeline


@dataclass
class JobRecord:
    job_id: str
    source_language: str
    target_language: str
    source_video_path: Path
    speaker_wav_path: Optional[Path]
    status: JobStatus = JobStatus.queued
    progress: float = 0.0
    error: Optional[str] = None
    transcript: Optional[str] = None
    translated_text: Optional[str] = None
    output_path: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class JobManager:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pipeline = TranslationPipeline(settings)
        self._executor = ThreadPoolExecutor(max_workers=settings.max_workers)
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def create_job(
        self,
        video_filename: str,
        video_bytes: bytes,
        source_language: str,
        target_language: str,
        speaker_filename: Optional[str] = None,
        speaker_bytes: Optional[bytes] = None,
    ) -> JobRecord:
        job_id = str(uuid.uuid4())

        video_suffix = Path(video_filename).suffix or ".mp4"
        source_video_path = self._settings.uploads_dir / f"{job_id}{video_suffix}"
        source_video_path.write_bytes(video_bytes)

        speaker_wav_path = None
        if speaker_filename and speaker_bytes:
            speaker_suffix = Path(speaker_filename).suffix or ".wav"
            speaker_wav_path = self._settings.uploads_dir / f"{job_id}_speaker{speaker_suffix}"
            speaker_wav_path.write_bytes(speaker_bytes)

        record = JobRecord(
            job_id=job_id,
            source_language=source_language,
            target_language=target_language,
            source_video_path=source_video_path,
            speaker_wav_path=speaker_wav_path,
        )

        with self._lock:
            self._jobs[job_id] = record

        self._executor.submit(self._run_job, job_id)
        return record

    def _run_job(self, job_id: str) -> None:
        self._update(job_id, status=JobStatus.processing, progress=0.05)

        def update_progress(progress: float) -> None:
            self._update(job_id, progress=progress)

        try:
            job = self.get_job(job_id)
            result = self._pipeline.run(
                job_id=job_id,
                source_video_path=job.source_video_path,
                source_language=job.source_language,
                target_language=job.target_language,
                speaker_wav_path=job.speaker_wav_path,
                progress_cb=update_progress,
            )
            self._update(
                job_id,
                status=JobStatus.completed,
                progress=1.0,
                transcript=result.get("transcript"),
                translated_text=result.get("translated_text"),
                output_path=result.get("output_path"),
            )
        except Exception as exc:
            self._update(job_id, status=JobStatus.failed, error=str(exc))

    def _update(self, job_id: str, **changes) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for key, value in changes.items():
                setattr(job, key, value)
            job.updated_at = datetime.now(timezone.utc)

    def get_job(self, job_id: str) -> JobRecord:
        with self._lock:
            job = self._jobs.get(job_id)
        if not job:
            raise KeyError(f"Job not found: {job_id}")
        return job
