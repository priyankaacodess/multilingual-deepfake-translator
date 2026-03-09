from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Multilingual Deepfake Translator API"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])
    cors_origins_csv: str = ""

    storage_root: Path = Path("storage")
    uploads_dir: Path = Path("storage/uploads")
    outputs_dir: Path = Path("storage/outputs")
    tmp_dir: Path = Path("storage/tmp")

    pipeline_mode: str = Field(default="real", description="mock or real")
    max_workers: int = 2

    whisper_model: str = "medium"
    nllb_model: str = "facebook/nllb-200-distilled-600M"
    coqui_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    use_gpu: bool = False

    wav2lip_repo: Path = Path("models/Wav2Lip")
    wav2lip_checkpoint: Path = Path("models/wav2lip/wav2lip_gan.pth")
    wav2lip_python_bin: str = "python"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.cors_origins_csv.strip():
        settings.cors_origins = [origin.strip() for origin in settings.cors_origins_csv.split(",") if origin.strip()]
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)
    settings.tmp_dir.mkdir(parents=True, exist_ok=True)
    return settings
