import secrets
from abc import ABC, abstractmethod


class BaseOAuthService(ABC):
    platform_name = "base"

    @staticmethod
    def generate_state() -> str:
        return secrets.token_urlsafe(32)

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def get_simulation_auth_url(self, redirect_uri: str, state: str) -> str:
        return f"{redirect_uri}?code=sim_code_{self.platform_name}_{secrets.token_hex(8)}&state={state}"

    def simulate_token_exchange(self, code: str) -> dict:
        return {
            "access_token": f"sim_oauth_token_{self.platform_name}_{secrets.token_hex(16)}",
            "refresh_token": f"sim_refresh_{secrets.token_hex(16)}",
            "account_id": f"{self.platform_name}_user_{secrets.randbelow(999999)}",
            "account_name": f"@{self.platform_name}_creator",
            "expires_in": 3600,
        }

    @abstractmethod
    def get_authorization_url(self, redirect_uri: str, state: str, **kwargs) -> str:
        pass

    @abstractmethod
    def exchange_code(self, code: str, redirect_uri: str, **kwargs) -> dict:
        pass

