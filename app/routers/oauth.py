import secrets
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from app.dependencies import require_auth_page
from app.models.account import SocialAccountModel
from app.services.oauth.manager import OAuthManager
from app.flash import flash

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/{platform}/authorize")
async def oauth_authorize(platform: str, request: Request, user=Depends(require_auth_page)):
    platform = platform.lower()
    try:
        service = OAuthManager.get_service(platform)
    except ValueError as e:
        flash(request, str(e), "danger")
        return RedirectResponse("/", status_code=303)

    state = service.generate_state()
    request.session[f"oauth_state_{platform}"] = state
    redirect_uri = str(request.url_for("oauth_callback", platform=platform))

    kwargs = {}
    if platform == "twitter":
        verifier = secrets.token_urlsafe(48)
        request.session["oauth_verifier_twitter"] = verifier
        kwargs["code_challenge"] = service.generate_pkce_challenge(verifier)

    auth_url = service.get_authorization_url(redirect_uri, state, **kwargs)
    return RedirectResponse(auth_url, status_code=303)


@router.get("/{platform}/callback", name="oauth_callback")
async def oauth_callback(platform: str, request: Request, user=Depends(require_auth_page)):
    platform = platform.lower()
    user_id = user["id"]

    error = request.query_params.get("error")
    if error:
        desc = request.query_params.get("error_description", error)
        flash(request, f"{platform.capitalize()} connection declined: {desc}", "warning")
        return RedirectResponse("/", status_code=303)

    state = request.query_params.get("state")
    expected_state = request.session.pop(f"oauth_state_{platform}", None)
    if not state or state != expected_state:
        flash(request, "OAuth security state mismatch (CSRF detected).", "danger")
        return RedirectResponse("/", status_code=303)

    code = request.query_params.get("code")
    if not code:
        flash(request, "Authorization code missing from provider callback.", "danger")
        return RedirectResponse("/", status_code=303)

    redirect_uri = str(request.url_for("oauth_callback", platform=platform))
    kwargs = {}
    if platform == "twitter":
        kwargs["code_verifier"] = request.session.pop("oauth_verifier_twitter", "")

    try:
        service = OAuthManager.get_service(platform)
        token_data = service.exchange_code(code, redirect_uri, **kwargs)

        SocialAccountModel.create_or_update(
            user_id=user_id,
            platform=platform,
            account_name=token_data.get("account_name", f"@{platform}_user"),
            token=token_data["access_token"],
            account_id=token_data.get("account_id", ""),
            refresh_token=token_data.get("refresh_token", ""),
        )
        flash(request, f"Connected {platform.capitalize()} ({token_data.get('account_name')}) via OAuth!", "success")
    except Exception as e:
        flash(request, f"OAuth connection failed for {platform.capitalize()}: {str(e)}", "danger")

    return RedirectResponse("/", status_code=303)

