import requests
from app.services.platforms.base import BasePlatformPublisher


class TikTokPublisher(BasePlatformPublisher):
    platform_name = "tiktok"
    API_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"

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
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=UTF-8",
            }
            # TikTok Direct Post API expects video initialization payload
            payload = {
                "post_info": {
                    "title": text[:150],  # TikTok title limit
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_stitch": False,
                    "disable_comment": False,
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": media_path,
                },
            }

            res = requests.post(self.API_URL, json=payload, headers=headers, timeout=30)
            res_data = res.json()

            if res_data.get("error", {}).get("code") == "ok":
                publish_id = res_data.get("data", {}).get("publish_id", "tiktok_ok")
                return {
                    "success": True,
                    "platform_post_id": publish_id,
                    "error": None,
                }
            err_msg = res_data.get("error", {}).get("message", "TikTok posting failed")
            return {"success": False, "platform_post_id": None, "error": err_msg}
        except Exception as e:
            return {"success": False, "platform_post_id": None, "error": str(e)}

