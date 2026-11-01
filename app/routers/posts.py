import os
import json
import time
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse, FileResponse
from werkzeug.utils import secure_filename
from app.dependencies import require_auth_api
from app.models.account import SocialAccountModel
from app.models.post import PostModel
from app.services.publisher import MultiPlatformPublisher
from app.config import Config

router = APIRouter(prefix="/posts", tags=["posts"])


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


def get_media_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[1].lower()
    return "video" if ext in Config.ALLOWED_VIDEO_EXTENSIONS else "image"


@router.post("/publish")
async def publish_post(
    media_file: UploadFile = File(None),
    media_filename: str = Form(""),
    master_caption: str = Form(""),
    platform_payloads: str = Form("{}"),
    user=Depends(require_auth_api),
):
    user_id = user["id"]
    filename = None
    upload_folder = str(Config.UPLOAD_FOLDER)
    os.makedirs(upload_folder, exist_ok=True)

    if media_file and media_file.filename and allowed_file(media_file.filename):
        raw_name = secure_filename(media_file.filename)
        filename = f"{user_id}_{int(time.time())}_{raw_name}"
        dest_path = os.path.join(upload_folder, filename)
        content = await media_file.read()
        with open(dest_path, "wb") as f:
            f.write(content)
    elif media_filename:
        filename = secure_filename(media_filename)
    else:
        return JSONResponse({"success": False, "error": "Valid media file (reel/video or image) is required."}, 400)

    media_type = get_media_type(filename)
    media_path = os.path.join(upload_folder, filename)

    try:
        payloads = json.loads(platform_payloads)
    except Exception:
        payloads = {}

    accounts = SocialAccountModel.list_by_user(user_id, active_only=True)
    if not accounts:
        return JSONResponse({"success": False, "error": "No active connected accounts found."}, 400)

    post_id = PostModel.create(user_id, filename, media_type, master_caption)
    dispatch_results = MultiPlatformPublisher.dispatch_all(
        accounts=accounts,
        media_path=media_path,
        media_type=media_type,
        master_caption=master_caption,
        platform_payloads=payloads,
        simulation_mode=Config.SIMULATION_MODE,
    )

    all_ok = True
    for res in dispatch_results:
        status = "success" if res.get("success") else "failed"
        if not res.get("success"):
            all_ok = False
        PostModel.add_log(
            post_id=post_id,
            platform=res.get("platform", "unknown"),
            status=status,
            platform_post_id=res.get("platform_post_id"),
            caption_used=res.get("caption_used"),
            hashtags_used=res.get("hashtags_used"),
            error_message=res.get("error"),
        )

    overall_status = "published" if all_ok else "partial"
    PostModel.update_status(post_id, overall_status)

    return {
        "success": True,
        "post_id": post_id,
        "overall_status": overall_status,
        "results": dispatch_results,
    }


@router.get("/uploads/{filename}")
async def serve_upload(filename: str, user=Depends(require_auth_api)):
    safe_name = secure_filename(filename)
    file_path = os.path.join(str(Config.UPLOAD_FOLDER), safe_name)
    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, 404)
    return FileResponse(file_path)

