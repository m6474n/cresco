import requests
from app.services.platforms.base import BasePlatformPublisher


class InstagramPublisher(BasePlatformPublisher):
    platform_name = "instagram"
    GRAPH_API = "https://graph.facebook.com/v19.0"

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
        ig_user_id = account.get("account_id") or "me"

        try:
            # 1. Create Media Container
            container_url = f"{self.GRAPH_API}/{ig_user_id}/media"
            params = {
                "access_token": token,
                "caption": text,
            }

            if media_type == "video":
                params["media_type"] = "REELS"
                params["video_url"] = media_path  # Must be public URL in production
            else:
                params["image_url"] = media_path

            res = requests.post(container_url, data=params, timeout=30)
            res_data = res.json()
            if "id" not in res_data:
                return {
                    "success": False,
                    "platform_post_id": None,
                    "error": res_data.get("error", {}).get("message", "Container creation failed"),
                }

            creation_id = res_data["id"]

            # 2. Publish Container
            publish_url = f"{self.GRAPH_API}/{ig_user_id}/media_publish"
            pub_res = requests.post(
                publish_url,
                data={"creation_id": creation_id, "access_token": token},
                timeout=30,
            )
            pub_data = pub_res.json()

            if "id" in pub_data:
                return {
                    "success": True,
                    "platform_post_id": pub_data["id"],
                    "error": None,
                }
            return {
                "success": False,
                "platform_post_id": None,
                "error": pub_data.get("error", {}).get("message", "Publish failed"),
            }
        except Exception as e:
            return {"success": False, "platform_post_id": None, "error": str(e)}

