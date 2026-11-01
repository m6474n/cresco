import sqlite3
import threading
from app.config import Config

_thread_local = threading.local()


def get_db(db_path=None):
    if not hasattr(_thread_local, "connection") or _thread_local.connection is None:
        path = db_path or Config.DATABASE_PATH
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        _thread_local.connection = conn
    return _thread_local.connection


def close_db():
    conn = getattr(_thread_local, "connection", None)
    if conn is not None:
        conn.close()
        _thread_local.connection = None


def init_db(db_path=None):
    path = db_path or Config.DATABASE_PATH
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS social_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            account_name TEXT NOT NULL,
            account_id TEXT,
            encrypted_token TEXT NOT NULL,
            encrypted_secret TEXT,
            encrypted_refresh_token TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE (user_id, platform, account_name)
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            media_filename TEXT NOT NULL,
            media_type TEXT NOT NULL,
            master_caption TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS post_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            platform_post_id TEXT,
            caption_used TEXT,
            hashtags_used TEXT,
            status TEXT NOT NULL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()
