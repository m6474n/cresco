import urllib.parse
import requests
from app.config import Config
from app.services.oauth.base import BaseOAuthService


class InstagramOAuthService(BaseOAuthService):
    platform_name = "instagram"
    AUTH_URL = "https://www.facebook.com/v19.0/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/v19.0/oauth/access_token"
    SCOPES = ["instagram_basic", "instagram_content_publish", "pages_show_list"]

    def __init__(self):
        self.client_id = Config.INSTAGRAM_APP_ID
        self.client_secret = Config.INSTAGRAM_APP_SECRET

    def get_authorization_url(self, redirect_uri: str, state: str, **kwargs) -> str:
        if Config.SIMULATION_MODE or not self.is_configured():
            return self.get_simulation_auth_url(redirect_uri, state)

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": ",".join(self.SCOPES),
            "response_type": "code",
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str, redirect_uri: str, **kwargs) -> dict:
        if code.startswith("sim_code_") or not self.is_configured():
            return self.simulate_token_exchange(code)

        res = requests.get(
            self.TOKEN_URL,
            params={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": redirect_uri,
                "code": code,
            },
            timeout=20,
        )
        data = res.json()
        if "access_token" not in data:
            raise ValueError(data.get("error", {}).get("message", "Instagram OAuth failed"))

        token = data["access_token"]
        user_res = requests.get(
            "https://graph.facebook.com/v19.0/me/accounts",
            params={"access_token": token, "fields": "instagram_business_account{id,username}"},
            timeout=20,
        ).json()

        ig_data = user_res.get("data", [{}])[0].get("instagram_business_account", {})
        return {
            "access_token": token,
            "account_id": ig_data.get("id", "me"),
            "account_name": f"@{ig_data.get('username', 'instagram_user')}",
            "refresh_token": "",
            "expires_in": data.get("expires_in", 5184000),
        }
