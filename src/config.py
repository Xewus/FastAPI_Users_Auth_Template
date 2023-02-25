from pathlib import Path

from pydantic import BaseSettings

ROOT_DIR = Path(__file__).parent.parent.resolve()

MEDIA_DIR = ROOT_DIR / 'media'
AVATARS_DIR = MEDIA_DIR / 'avatars'

AVATAR_SIZES = [(400, 400), (100, 100), (50, 50)]


class AppSettings(BaseSettings):
    """Get settings from `.env` file.

    Use uppercase for the names of the values in the file.
    """
    debug: bool = False
    path: str  # ENV PATH from os
    app_title: str = 'Template'
    secret_key: str = ',gcf975'  # salt for hashing password
    algorithm: str = 'HS256'  # algorithm for hashing password
    access_token_expire_minutes: int = 60
    database_url: str = 'sqlite+aiosqlite:///./sqlite.db'

    class Config:
        env_file = '.env'


settings = AppSettings()
