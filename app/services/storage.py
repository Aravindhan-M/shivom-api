import os
from pathlib import Path
from uuid import uuid4

from ..config import Settings

settings = Settings()


def save_file(file_bytes: bytes, filename: str, subdir: str = "") -> str:
    dest_dir = Path(settings.MEDIA_ROOT) / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid4().hex}_{filename}"
    dest_path = dest_dir / unique_name
    with open(dest_path, "wb") as f:
        f.write(file_bytes)
    return str(dest_path)


def get_file_url(path: str) -> str:
    # For local storage we expose files under /media
    return f"/media/{os.path.relpath(path, settings.MEDIA_ROOT)}"
