from abc import ABC, abstractmethod
import time
import random


class BasePlatformPublisher(ABC):
    platform_name = "base"

    def combine_content(self, caption: str, hashtags: str) -> str:
        parts = []
        if caption and caption.strip():
            parts.append(caption.strip())
        if hashtags and hashtags.strip():
            parts.append(hashtags.strip())
        return "\n\n".join(parts)

    def simulate_publish(self, account: dict, caption: str, hashtags: str) -> dict:
        time.sleep(0.3)
        mock_id = f"{self.platform_name}_post_{int(time.time())}_{random.randint(1000, 9999)}"
        return {
            "success": True,
            "platform_post_id": mock_id,
            "error": None,
            "simulated": True,
        }

    @abstractmethod
    def publish(
        self,
        account: dict,
        media_path: str,
        media_type: str,
        caption: str,
        hashtags: str,
        simulation_mode: bool = False,
    ) -> dict:
        """Publishes media to the target platform and returns dict with success, platform_post_id, error"""
        pass

