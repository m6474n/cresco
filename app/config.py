import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-secret-change-me")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
    DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "content_studio.db")
    UPLOAD_FOLDER = BASE_DIR / os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", str(100 * 1024 * 1024))
    )
    SIMULATION_MODE = os.getenv("SIMULATION_MODE", "True").lower() in (
        "true",
        "1",
        "yes",
    )

    ALLOWED_EXTENSIONS = {
        "mp4",
        "mov",
        "avi",
        "webm",
        "jpg",
        "jpeg",
        "png",
        "webp",
    }
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "webm"}
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

    # Security headers & Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Set to True in production HTTPS
    PERMANENT_SESSION_LIFETIME = 86400 * 7

    # Platform settings
    INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID", "")
    INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET", "")
    TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
    TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
    FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "")
    FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")
    THREADS_APP_ID = os.getenv("THREADS_APP_ID", "")
    THREADS_APP_SECRET = os.getenv("THREADS_APP_SECRET", "")
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

