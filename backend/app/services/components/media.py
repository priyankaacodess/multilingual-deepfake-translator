import subprocess
from pathlib import Path


class MediaProcessingError(RuntimeError):
    pass


def run_command(command: list[str]) -> None:
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise MediaProcessingError(completed.stderr.strip() or "Command failed")


def extract_audio_from_video(video_path: Path, audio_path: Path) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-ar",
        "16000",
        "-ac",
        "1",
        "-vn",
        str(audio_path),
    ]
    run_command(command)
