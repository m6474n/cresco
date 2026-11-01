from app.database import get_db


class PostModel:
    @staticmethod
    def create(user_id: int, media_filename: str, media_type: str, master_caption: str):
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO posts (user_id, media_filename, media_type, master_caption, status)
            VALUES (?, ?, ?, ?, 'processing')
            """,
            (user_id, media_filename, media_type, master_caption),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update_status(post_id: int, status: str):
        db = get_db()
        db.execute("UPDATE posts SET status = ? WHERE id = ?", (status, post_id))
        db.commit()

    @staticmethod
    def add_log(
        post_id: int,
        platform: str,
        status: str,
        platform_post_id: str = None,
        caption_used: str = None,
        hashtags_used: str = None,
        error_message: str = None,
    ):
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO post_logs
                (post_id, platform, platform_post_id, caption_used,
                 hashtags_used, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post_id,
                platform.lower(),
                platform_post_id,
                caption_used,
                hashtags_used,
                status,
                error_message,
            ),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_user_posts_with_logs(user_id: int, limit: int = 15):
        db = get_db()
        posts = db.execute(
            """
            SELECT * FROM posts WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

        results = []
        for post in posts:
            p = dict(post)
            logs = db.execute(
                """
                SELECT * FROM post_logs WHERE post_id = ?
                ORDER BY created_at ASC
                """,
                (p["id"],),
            ).fetchall()
            p["logs"] = [dict(log) for log in logs]
            results.append(p)
        return results

