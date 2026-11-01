import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send
from app.config import Config
from app.database import init_db
from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.accounts import router as accounts_router
from app.routers.oauth import router as oauth_router
from app.routers.posts import router as posts_router


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-content-type-options", b"nosniff"))
                headers.append((b"x-frame-options", b"DENY"))
                headers.append((b"x-xss-protection", b"1; mode=block"))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(str(Config.UPLOAD_FOLDER), exist_ok=True)
    init_db()
    yield


app = FastAPI(title="Cresco Studio API", version="1.0.0", lifespan=lifespan)

# Add middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=Config.SECRET_KEY,
    max_age=Config.PERMANENT_SESSION_LIFETIME,
    same_site=Config.SESSION_COOKIE_SAMESITE.lower(),
    https_only=Config.SESSION_COOKIE_SECURE,
)

# Mount static assets
static_path = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers
app.include_router(dashboard_router)
app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(oauth_router)
app.include_router(posts_router)
