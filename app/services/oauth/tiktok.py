import urllib.parse
import requests
from app.config import Config
from app.services.oauth.base import BaseOAuthService


class TikTokOAuthService(BaseOAuthService):
    platform_name = "tiktok"
    AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
    TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
    USER_INFO_URL = "https://open.tiktokapis.com/v2/user/info/"
    SCOPES = ["user.info.basic", "video.upload", "video.publish"]

    def __init__(self):
        self.client_id = Config.TIKTOK_CLIENT_KEY
        self.client_secret = Config.TIKTOK_CLIENT_SECRET

    def get_authorization_url(self, redirect_uri: str, state: str, **kwargs) -> str:
        if Config.SIMULATION_MODE or not self.is_configured():
            return self.get_simulation_auth_url(redirect_uri, state)

        params = {
            "client_key": self.client_id,
            "response_type": "code",
            "scope": ",".join(self.SCOPES),
            "redirect_uri": redirect_uri,
            "state": state,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str, redirect_uri: str, **kwargs) -> dict:
        if code.startswith("sim_code_") or not self.is_configured():
            return self.simulate_token_exchange(code)

        payload = {
            "client_key": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        res = requests.post(
            self.TOKEN_URL,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=20,
        )
        data = res.json()
        if "access_token" not in data:
            raise ValueError(data.get("message") or data.get("error_description", "TikTok OAuth exchange failed"))

        token = data["access_token"]
        open_id = data.get("open_id", "")

        profile_res = requests.get(
            self.USER_INFO_URL,
            headers={"Authorization": f"Bearer {token}"},
            params={"fields": "open_id,display_name,avatar_url"},
            timeout=20,
        ).json()

        display_name = profile_res.get("data", {}).get("user", {}).get("display_name", open_id or "tiktok_creator")
        return {
            "access_token": token,
            "account_id": open_id,
            "account_name": f"@{display_name}",
            "refresh_token": data.get("refresh_token", ""),
            "expires_in": data.get("expires_in", 86400),
        }
