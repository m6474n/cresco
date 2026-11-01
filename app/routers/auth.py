from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates_engine import templates
from app.models.user import UserModel
from app.flash import flash

router = APIRouter(tags=["auth"])


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request=request, name="auth.html", context={"mode": "register"})


@router.post("/register")
async def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    email = email.strip().lower()
    password = password.strip()

    if not email or not password:
        flash(request, "Email and password are required.", "danger")
    elif len(password) < 8:
        flash(request, "Password must be at least 8 characters.", "danger")
    elif password != confirm_password:
        flash(request, "Passwords do not match.", "danger")
    elif UserModel.find_by_email(email):
        flash(request, "An account with this email already exists.", "danger")
    else:
        user_id = UserModel.create(email, password)
        request.session.clear()
        request.session["user_id"] = user_id
        request.session["user_email"] = email
        flash(request, "Welcome to Content Studio!", "success")
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(request=request, name="auth.html", context={"mode": "register"})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request=request, name="auth.html", context={"mode": "login"})


@router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    email = email.strip().lower()
    user = UserModel.find_by_email(email)
    if user and UserModel.verify_password(user["password_hash"], password):
        request.session.clear()
        request.session["user_id"] = user["id"]
        request.session["user_email"] = user["email"]
        flash(request, "Signed in successfully.", "success")
        return RedirectResponse("/", status_code=303)

    flash(request, "Invalid email or password.", "danger")
    return templates.TemplateResponse(request=request, name="auth.html", context={"mode": "login"})


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    flash(request, "You have been logged out.", "info")
    return RedirectResponse("/login", status_code=303)

