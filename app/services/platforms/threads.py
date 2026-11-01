import requests
from app.services.platforms.base import BasePlatformPublisher


class ThreadsPublisher(BasePlatformPublisher):
    platform_name = "threads"
    THREADS_API = "https://graph.threads.net/v1.0"

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
        user_id = account.get("account_id") or "me"

        try:
            # 1. Create Threads Media Container
            container_url = f"{self.THREADS_API}/{user_id}/threads"
            payload = {
                "access_token": token,
                "text": text,
            }
            if media_type == "video":
                payload["media_type"] = "VIDEO"
                payload["video_url"] = media_path
            else:
                payload["media_type"] = "IMAGE"
                payload["image_url"] = media_path

            res = requests.post(container_url, data=payload, timeout=30)
            res_data = res.json()
            if "id" not in res_data:
                err = res_data.get("error", {}).get("message", "Threads container creation failed")
                return {"success": False, "platform_post_id": None, "error": err}

            creation_id = res_data["id"]

            # 2. Publish Threads Container
            publish_url = f"{self.THREADS_API}/{user_id}/threads_publish"
            pub_res = requests.post(
                publish_url,
                data={"creation_id": creation_id, "access_token": token},
                timeout=30,
            )
            pub_data = pub_res.json()
            if "id" in pub_data:
                return {"success": True, "platform_post_id": pub_data["id"], "error": None}

            err = pub_data.get("error", {}).get("message", "Threads publish failed")
            return {"success": False, "platform_post_id": None, "error": err}
        except Exception as e:
            return {"success": False, "platform_post_id": None, "error": str(e)}

