from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from app.models.user import UserModel


def get_current_user_optional(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return UserModel.find_by_id(user_id)


def require_auth_page(request: Request):
    user = get_current_user_optional(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"},
        )
    return user


def require_auth_api(request: Request):
    user = get_current_user_optional(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user

