import requests
from app.services.platforms.base import BasePlatformPublisher


class FacebookPublisher(BasePlatformPublisher):
    platform_name = "facebook"
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
        page_id = account.get("account_id") or "me"

        try:
            endpoint = f"{self.GRAPH_API}/{page_id}/videos" if media_type == "video" else f"{self.GRAPH_API}/{page_id}/photos"
            params = {
                "access_token": token,
                "description" if media_type == "video" else "caption": text,
            }

            if media_path.startswith("http"):
                params["file_url" if media_type == "video" else "url"] = media_path
                res = requests.post(endpoint, data=params, timeout=40)
            else:
                field_name = "source"
                with open(media_path, "rb") as media_file:
                    files = {field_name: media_file}
                    res = requests.post(endpoint, data=params, files=files, timeout=60)

            res_data = res.json()
            post_id = res_data.get("id") or res_data.get("post_id")
            if post_id:
                return {
                    "success": True,
                    "platform_post_id": str(post_id),
                    "error": None,
                }

            error = res_data.get("error", {}).get("message", "Facebook publish failed")
            return {"success": False, "platform_post_id": None, "error": error}
        except Exception as e:
            return {"success": False, "platform_post_id": None, "error": str(e)}

