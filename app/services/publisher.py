from concurrent.futures import ThreadPoolExecutor
from app.services.platforms.instagram import InstagramPublisher
from app.services.platforms.tiktok import TikTokPublisher
from app.services.platforms.facebook import FacebookPublisher
from app.services.platforms.threads import ThreadsPublisher
from app.services.platforms.twitter import TwitterPublisher


class MultiPlatformPublisher:
    PUBLISHERS = {
        "instagram": InstagramPublisher(),
        "tiktok": TikTokPublisher(),
        "facebook": FacebookPublisher(),
        "threads": ThreadsPublisher(),
        "twitter": TwitterPublisher(),
    }

    @classmethod
    def dispatch_single(
        cls,
        account: dict,
        media_path: str,
        media_type: str,
        caption: str,
        hashtags: str,
        simulation_mode: bool,
    ) -> dict:
        platform = account.get("platform", "").lower()
        publisher = cls.PUBLISHERS.get(platform)
        if not publisher:
            return {
                "platform": platform,
                "account_name": account.get("account_name"),
                "success": False,
                "platform_post_id": None,
                "error": f"Unsupported platform: {platform}",
            }

        result = publisher.publish(
            account=account,
            media_path=media_path,
            media_type=media_type,
            caption=caption,
            hashtags=hashtags,
            simulation_mode=simulation_mode,
        )
        result["platform"] = platform
        result["account_name"] = account.get("account_name")
        result["caption_used"] = caption
        result["hashtags_used"] = hashtags
        return result

    @classmethod
    def dispatch_all(
        cls,
        accounts: list,
        media_path: str,
        media_type: str,
        master_caption: str,
        platform_payloads: dict,
        simulation_mode: bool = True,
    ) -> list:
        results = []

        def task(account):
            plat = account.get("platform", "").lower()
            overrides = platform_payloads.get(plat, {})
            caption = overrides.get("caption") or master_caption or ""
            hashtags = overrides.get("hashtags") or ""
            return cls.dispatch_single(
                account=account,
                media_path=media_path,
                media_type=media_type,
                caption=caption,
                hashtags=hashtags,
                simulation_mode=simulation_mode,
            )

        with ThreadPoolExecutor(max_workers=min(len(accounts) or 1, 5)) as executor:
            futures = [executor.submit(task, acc) for acc in accounts]
            for future in futures:
                try:
                    results.append(future.result())
                except Exception as err:
                    results.append(
                        {
                            "platform": "unknown",
                            "success": False,
                            "error": str(err),
                        }
                    )
        return results

