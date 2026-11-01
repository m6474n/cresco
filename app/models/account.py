from app.database import get_db
from app.services.crypto import CryptoService


class SocialAccountModel:
    SUPPORTED_PLATFORMS = ["instagram", "tiktok", "facebook", "threads", "twitter"]

    @staticmethod
    def create_or_update(
        user_id: int,
        platform: str,
        account_name: str,
        token: str,
        account_id: str = "",
        secret: str = "",
        refresh_token: str = "",
    ):
        db = get_db()
        enc_token = CryptoService.encrypt(token)
        enc_secret = CryptoService.encrypt(secret) if secret else ""
        enc_refresh = CryptoService.encrypt(refresh_token) if refresh_token else ""

        db.execute(
            """
            INSERT INTO social_accounts
                (user_id, platform, account_name, account_id, encrypted_token,
                 encrypted_secret, encrypted_refresh_token, is_active, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, platform, account_name) DO UPDATE SET
                account_id = excluded.account_id,
                encrypted_token = excluded.encrypted_token,
                encrypted_secret = excluded.encrypted_secret,
                encrypted_refresh_token = excluded.encrypted_refresh_token,
                is_active = 1,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, platform.lower(), account_name, account_id, enc_token, enc_secret, enc_refresh),
        )
        db.commit()

    @staticmethod
    def list_by_user(user_id: int, active_only: bool = False):
        db = get_db()
        sql = "SELECT * FROM social_accounts WHERE user_id = ?"
        params = [user_id]
        if active_only:
            sql += " AND is_active = 1"
        sql += " ORDER BY platform ASC, created_at DESC"
        rows = db.execute(sql, params).fetchall()

        results = []
        for row in rows:
            acc = dict(row)
            acc["decrypted_token"] = CryptoService.decrypt(acc["encrypted_token"])
            acc["decrypted_secret"] = (
                CryptoService.decrypt(acc["encrypted_secret"]) if acc["encrypted_secret"] else ""
            )
            results.append(acc)
        return results

    @staticmethod
    def toggle_active(account_id: int, user_id: int):
        db = get_db()
        db.execute(
            "UPDATE social_accounts SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ? AND user_id = ?",
            (account_id, user_id),
        )
        db.commit()

    @staticmethod
    def delete(account_id: int, user_id: int):
        db = get_db()
        db.execute(
            "DELETE FROM social_accounts WHERE id = ? AND user_id = ?",
            (account_id, user_id),
        )
        db.commit()

