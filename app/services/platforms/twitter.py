import requests
from app.services.platforms.base import BasePlatformPublisher


class TwitterPublisher(BasePlatformPublisher):
    platform_name = "twitter"
    TWEET_URL = "https://api.twitter.com/2/tweets"

    def publish(
        self,
        account: dict,
        media_path: str,
        media_type: str,
        caption: str,
        hashtags: str,
        simulation_mode: bool = False,
    ) -> dict:
        if simulation_mode or not account.get("decrypted_token"):
            return self.simulate_publish(account, caption, hashtags)

        text = self.combine_content(caption, hashtags)
        token = account["decrypted_token"]

        try:
            # Twitter API v2 POST /2/tweets
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            # Enforce 280 character limit for standard X tweets
            tweet_text = text[:280] if len(text) > 280 else text
            payload = {"text": tweet_text}

            res = requests.post(self.TWEET_URL, json=payload, headers=headers, timeout=30)
            res_data = res.json()

            if res.status_code in (200, 201) and "data" in res_data:
                return {
                    "success": True,
                    "platform_post_id": res_data["data"]["id"],
                    "error": None,
                }

            error_msg = res_data.get("detail") or res_data.get("title", "Twitter posting failed")
            return {"success": False, "platform_post_id": None, "error": error_msg}
        except Exception as e:
            return {"success": False, "platform_post_id": None, "error": str(e)}

