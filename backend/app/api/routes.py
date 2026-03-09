from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.core.config import Settings, get_settings
from app.models.schemas import CreateJobResponse, JobDetailResponse, LanguagesResponse, LanguageOption
from app.services.job_manager import JobManager
from app.utils.lang_map import SUPPORTED_LANGUAGES, get_language

router = APIRouter()
_job_manager: Optional[JobManager] = None


def get_job_manager(settings: Settings = Depends(get_settings)) -> JobManager:
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager(settings)
    return _job_manager


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/languages", response_model=LanguagesResponse)
def languages() -> LanguagesResponse:
    options = [
        LanguageOption(code=spec.code, name=spec.name)
        for spec in sorted(SUPPORTED_LANGUAGES.values(), key=lambda item: item.name)
    ]
    return LanguagesResponse(source_languages=options, target_languages=options)


@router.post("/jobs", response_model=CreateJobResponse)
async def create_job(
    source_language: str = Form(...),
    target_language: str = Form(...),
    video: UploadFile = File(...),
    speaker_wav: Optional[UploadFile] = File(default=None),
    manager: JobManager = Depends(get_job_manager),
) -> CreateJobResponse:
    try:
        get_language(source_language)
        get_language(target_language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    video_bytes = await video.read()
    if not video_bytes:
        raise HTTPException(status_code=400, detail="Uploaded video is empty")

    speaker_bytes = None
    speaker_name = None
    if speaker_wav is not None:
        speaker_bytes = await speaker_wav.read()
        if speaker_bytes:
            speaker_name = speaker_wav.filename or "speaker.wav"

    job = manager.create_job(
        video_filename=video.filename or "input.mp4",
        video_bytes=video_bytes,
        source_language=source_language,
        target_language=target_language,
        speaker_filename=speaker_name,
        speaker_bytes=speaker_bytes,
    )
    return CreateJobResponse(job_id=job.job_id, status=job.status)


@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
def get_job_status(
    job_id: str,
    request: Request,
    manager: JobManager = Depends(get_job_manager),
) -> JobDetailResponse:
    try:
        job = manager.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    output_url = None
    if job.output_path:
        output_url = str(request.url_for("download_result", job_id=job_id))

    return JobDetailResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        source_language=job.source_language,
        target_language=job.target_language,
        created_at=job.created_at,
        updated_at=job.updated_at,
        error=job.error,
        transcript=job.transcript,
        translated_text=job.translated_text,
        output_url=output_url,
    )


@router.get("/jobs/{job_id}/download", name="download_result")
def download_result(job_id: str, manager: JobManager = Depends(get_job_manager)) -> FileResponse:
    try:
        job = manager.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not job.output_path:
        raise HTTPException(status_code=404, detail="Result not available yet")

    return FileResponse(path=job.output_path, filename=f"translated_{job_id}.mp4", media_type="video/mp4")
