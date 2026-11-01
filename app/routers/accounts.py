from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from app.dependencies import require_auth_api
from app.models.account import SocialAccountModel
from app.flash import flash
from app.config import Config

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/connect")
async def connect_account(
    request: Request,
    platform: str = Form(...),
    account_name: str = Form(""),
    access_token: str = Form(""),
    account_id: str = Form(""),
    user=Depends(require_auth_api),
):
    platform = platform.strip().lower()
    user_id = user["id"]

    if platform not in SocialAccountModel.SUPPORTED_PLATFORMS:
        flash(request, "Invalid platform specified.", "danger")
        return RedirectResponse("/", status_code=303)

    if Config.SIMULATION_MODE and not access_token:
        access_token = f"sim_token_{platform}_{user_id}"
        if not account_name:
            account_name = f"@{platform}_creator"

    if not account_name:
        flash(request, "Account name/handle is required.", "danger")
        return RedirectResponse("/", status_code=303)

    try:
        SocialAccountModel.create_or_update(
            user_id=user_id,
            platform=platform,
            account_name=account_name,
            token=access_token,
            account_id=account_id,
        )
        flash(request, f"Connected {platform.capitalize()} ({account_name}).", "success")
    except Exception as e:
        flash(request, f"Failed to connect account: {str(e)}", "danger")

    return RedirectResponse("/", status_code=303)


@router.post("/{account_id}/toggle")
async def toggle_account(account_id: int, request: Request, user=Depends(require_auth_api)):
    SocialAccountModel.toggle_active(account_id, user["id"])
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JSONResponse({"success": True})
    return RedirectResponse("/", status_code=303)


@router.post("/{account_id}/disconnect")
async def disconnect_account(account_id: int, request: Request, user=Depends(require_auth_api)):
    SocialAccountModel.delete(account_id, user["id"])
    flash(request, "Account disconnected successfully.", "info")
    return RedirectResponse("/", status_code=303)

