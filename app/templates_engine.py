from pathlib import Path
import jinja2
from fastapi.templating import Jinja2Templates
from app.flash import get_flashed_messages as _get_flashed_messages

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def url_for_compat(name: str, **kwargs) -> str:
    routes_map = {
        "auth.login": "/login",
        "auth.register": "/register",
        "auth.logout": "/logout",
        "dashboard.index": "/",
        "accounts.connect": "/accounts/connect",
    }
    if name == "static":
        filename = kwargs.get("filename") or kwargs.get("path", "")
        return f"/static/{filename}"
    if name == "oauth.authorize":
        return f"/oauth/{kwargs.get('platform')}/authorize"
    if name == "oauth.callback":
        return f"/oauth/{kwargs.get('platform')}/callback"
    if name == "accounts.toggle":
        return f"/accounts/{kwargs.get('account_id')}/toggle"
    if name == "accounts.disconnect":
        return f"/accounts/{kwargs.get('account_id')}/disconnect"
    return routes_map.get(name, f"/{name}")


@jinja2.pass_context
def jinja_flashed_messages(context, with_categories=True):
    request = context.get("request")
    if not request:
        return []
    return _get_flashed_messages(request, with_categories=with_categories)


templates.env.globals["url_for"] = url_for_compat
templates.env.globals["get_flashed_messages"] = jinja_flashed_messages
