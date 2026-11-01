import hashlib
import base64
import urllib.parse
import requests
from app.config import Config
from app.services.oauth.base import BaseOAuthService


class TwitterOAuthService(BaseOAuthService):
    platform_name = "twitter"
    AUTH_URL = "https://twitter.com/i/oauth2/authorize"
    TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
    USER_INFO_URL = "https://api.twitter.com/2/users/me"
    SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access"]

    def __init__(self):
        self.client_id = Config.TWITTER_API_KEY
        self.client_secret = Config.TWITTER_API_SECRET

    @staticmethod
    def generate_pkce_challenge(verifier: str) -> str:
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    def get_authorization_url(self, redirect_uri: str, state: str, **kwargs) -> str:
        if Config.SIMULATION_MODE or not self.client_id:
            return self.get_simulation_auth_url(redirect_uri, state)

        code_challenge = kwargs.get("code_challenge", "")
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str, redirect_uri: str, **kwargs) -> dict:
        if code.startswith("sim_code_") or not self.client_id:
            return self.simulate_token_exchange(code)

        code_verifier = kwargs.get("code_verifier", "")
        payload = {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        auth = (self.client_id, self.client_secret) if self.client_secret else None

        res = requests.post(self.TOKEN_URL, data=payload, headers=headers, auth=auth, timeout=20)
        data = res.json()

        if "access_token" not in data:
            raise ValueError(data.get("error_description", "Twitter OAuth failed"))

        token = data["access_token"]
        user_res = requests.get(
            self.USER_INFO_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        ).json()
        u_data = user_res.get("data", {})

        return {
            "access_token": token,
            "account_id": u_data.get("id", ""),
            "account_name": f"@{u_data.get('username', 'x_creator')}",
            "refresh_token": data.get("refresh_token", ""),
            "expires_in": data.get("expires_in", 7200),
        }
