from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates_engine import templates
from app.dependencies import get_current_user_optional
from app.models.account import SocialAccountModel
from app.models.post import PostModel
from app.config import Config

router = APIRouter(tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
async def dashboard_view(request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse("/login", status_code=303)

    user_id = user["id"]
    accounts = SocialAccountModel.list_by_user(user_id)
    connected_platforms = {acc["platform"]: acc for acc in accounts if acc["is_active"]}
    supported = SocialAccountModel.SUPPORTED_PLATFORMS
    recent_posts = PostModel.get_user_posts_with_logs(user_id, limit=8)

    context = {
        "request": request,
        "session": request.session,
        "user_email": user["email"],
        "accounts": accounts,
        "connected_platforms": connected_platforms,
        "supported_platforms": supported,
        "recent_posts": recent_posts,
        "simulation_mode": Config.SIMULATION_MODE,
    }
    return templates.TemplateResponse(request=request, name="dashboard.html", context=context)

