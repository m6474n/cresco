from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db


class UserModel:
    @staticmethod
    def create(email: str, password: str):
        db = get_db()
        password_hash = generate_password_hash(password)
        cursor = db.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email.strip().lower(), password_hash),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def find_by_email(email: str):
        db = get_db()
        return db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()

    @staticmethod
    def find_by_id(user_id: int):
        db = get_db()
        return db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        return check_password_hash(stored_hash, password)

