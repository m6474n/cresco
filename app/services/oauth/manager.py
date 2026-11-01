from app.services.oauth.instagram import InstagramOAuthService
from app.services.oauth.tiktok import TikTokOAuthService
from app.services.oauth.facebook import FacebookOAuthService
from app.services.oauth.threads import ThreadsOAuthService
from app.services.oauth.twitter import TwitterOAuthService


class OAuthManager:
    _SERVICES = {
        "instagram": InstagramOAuthService,
        "tiktok": TikTokOAuthService,
        "facebook": FacebookOAuthService,
        "threads": ThreadsOAuthService,
        "twitter": TwitterOAuthService,
    }

    @classmethod
    def get_service(cls, platform: str):
        service_cls = cls._SERVICES.get(platform.lower())
        if not service_cls:
            raise ValueError(f"No OAuth provider configured for: {platform}")
        return service_cls()

