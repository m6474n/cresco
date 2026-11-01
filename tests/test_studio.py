import unittest
import io
import os
import urllib.parse
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.config import Config
from app.database import init_db, close_db
from app.models.user import UserModel
from app.models.account import SocialAccountModel
from app.models.post import PostModel
from app.services.crypto import CryptoService

TEST_DB_PATH = Path("test_content_studio.db")


class FastAPICrescoTestCase(unittest.TestCase):
    def setUp(self):
        close_db()
        Config.DATABASE_PATH = TEST_DB_PATH
        Config.SIMULATION_MODE = True
        if TEST_DB_PATH.exists():
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass
        init_db(TEST_DB_PATH)
        self.client = TestClient(app)

    def tearDown(self):
        close_db()
        if TEST_DB_PATH.exists():
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass

    def test_crypto_encryption_decryption(self):
        token = "EAABwzLIX564BA...my_secret_token"
        enc = CryptoService.encrypt(token)
        self.assertNotEqual(token, enc)
        self.assertEqual(token, CryptoService.decrypt(enc))

    def test_user_creation_and_auth(self):
        uid = UserModel.create("creator@test.com", "Password123!")
        self.assertIsNotNone(uid)
        user = UserModel.find_by_email("creator@test.com")
        self.assertIsNotNone(user)
        self.assertTrue(UserModel.verify_password(user["password_hash"], "Password123!"))

    def test_one_click_publish_flow(self):
        self.client.post("/register", data={
            "email": "user@studio.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        user = UserModel.find_by_email("user@studio.com")
        for plat in ["instagram", "tiktok", "facebook", "threads", "twitter"]:
            SocialAccountModel.create_or_update(
                user_id=user["id"],
                platform=plat,
                account_name=f"@{plat}_test",
                token=f"test_token_{plat}",
            )

        files = {"media_file": ("test_reel.mp4", io.BytesIO(b"fake video data"), "video/mp4")}
        data = {
            "master_caption": "Awesome new reel launching today! 🔥",
            "platform_payloads": '{"instagram":{"caption":"IG exclusive","hashtags":"#reels"}}',
        }
        res = self.client.post("/posts/publish", data=data, files=files)
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body["success"])
        self.assertEqual(len(body["results"]), 5)
        self.assertEqual(len(PostModel.get_user_posts_with_logs(user["id"])), 1)

    def test_oauth_flow_and_csrf_protection(self):
        self.client.post("/register", data={
            "email": "oauth@studio.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        # 1. Successful OAuth for Instagram
        auth_res = self.client.get("/oauth/instagram/authorize", follow_redirects=False)
        self.assertEqual(auth_res.status_code, 303)
        loc = auth_res.headers["location"]
        query = urllib.parse.parse_qs(urllib.parse.urlparse(loc).query)
        cb_res = self.client.get(
            f"/oauth/instagram/callback?code={query['code'][0]}&state={query['state'][0]}",
            follow_redirects=False,
        )
        self.assertEqual(cb_res.status_code, 303)

        # 2. Tampered state triggers CSRF error
        self.client.get("/oauth/tiktok/authorize", follow_redirects=False)
        csrf_res = self.client.get(
            "/oauth/tiktok/callback?code=sim_code&state=tampered_state",
            follow_redirects=True,
        )
        self.assertIn("CSRF detected", csrf_res.text)


if __name__ == "__main__":
    unittest.main()
