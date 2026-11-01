import urllib.parse
import requests
from app.config import Config
from app.services.oauth.base import BaseOAuthService


class ThreadsOAuthService(BaseOAuthService):
    platform_name = "threads"
    AUTH_URL = "https://threads.net/oauth/authorize"
    TOKEN_URL = "https://graph.threads.net/oauth/access_token"
    SCOPES = ["threads_basic", "threads_content_publish"]

    def __init__(self):
        self.client_id = Config.THREADS_APP_ID
        self.client_secret = Config.THREADS_APP_SECRET

    def get_authorization_url(self, redirect_uri: str, state: str, **kwargs) -> str:
        if Config.SIMULATION_MODE or not self.is_configured():
            return self.get_simulation_auth_url(redirect_uri, state)

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": ",".join(self.SCOPES),
            "response_type": "code",
            "state": state,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str, redirect_uri: str, **kwargs) -> dict:
        if code.startswith("sim_code_") or not self.is_configured():
            return self.simulate_token_exchange(code)

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code,
        }
        res = requests.post(self.TOKEN_URL, data=payload, timeout=20)
        data = res.json()

        if "access_token" not in data:
            raise ValueError(data.get("error_message", "Threads OAuth failed"))

        token = data["access_token"]
        user_id = str(data.get("user_id", "me"))

        info_res = requests.get(
            f"https://graph.threads.net/v1.0/{user_id}",
            params={"fields": "id,username", "access_token": token},
            timeout=20,
        ).json()

        username = info_res.get("username", user_id)
        return {
            "access_token": token,
            "account_id": user_id,
            "account_name": f"@{username}",
            "refresh_token": "",
            "expires_in": data.get("expires_in", 5184000),
        }
