from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.config import AVATARS_DIR, MEDIA_DIR, settings
from src.users.router import router as users_router

MEDIA_DIR.mkdir(exist_ok=True)
AVATARS_DIR.mkdir(exist_ok=True)

app = FastAPI(
    debug=settings.debug,
    title=settings.app_title,
    contact={'xewus': 'xewus@ya.ru'}
)
app.mount(str(MEDIA_DIR), StaticFiles(directory=MEDIA_DIR), 'media')
app.include_router(users_router, tags=('Users',))
