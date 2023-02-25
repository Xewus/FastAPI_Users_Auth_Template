from fastapi import FastAPI

from src.config import AVATARS_DIR, MEDIA_DIR, settings
from src.users.router import router as users_router

# MEDIA_DIR.mkdir(exist_ok=True)
# AVATARS_DIR.mkdir(exist_ok=True)

app = FastAPI(
    debug=settings.debug,
    title=settings.app_title,
    contact={'xewus': 'xewus@ya.ru'}
)

app.include_router(users_router, tags=('Users',))


@app.on_event('startup')
async def create_dirs():
    MEDIA_DIR.mkdir(exist_ok=True)
    AVATARS_DIR.mkdir(exist_ok=True)
