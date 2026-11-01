from fastapi import Request


def flash(request: Request, message: str, category: str = "info"):
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append((category, message))


def get_flashed_messages(request: Request, with_categories: bool = True):
    messages = request.session.pop("_messages", [])
    if with_categories:
        return messages
    return [msg for _, msg in messages]

