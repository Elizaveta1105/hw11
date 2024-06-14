from pathlib import Path
from urllib.request import Request

from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(Path(__file__).parent / 'templates'))


async def reset_password_item(request: Request, email: str):
    """
    Renders a password reset page for a given user.

    Args:
        request (Request): The request object.
        email (str): The email of the user who wants to reset their password.

    Returns:
        TemplateResponse: The rendered password reset page.
    """
    return templates.TemplateResponse(
        request=request, name="reset-page.html", context={"email": email}
    )



