from pathlib import Path
from urllib.request import Request

from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(Path(__file__).parent / 'templates'))


async def reset_password_item(request: Request, email: str):
    return templates.TemplateResponse(
        request=request, name="reset-page.html", context={"email": email}
    )



