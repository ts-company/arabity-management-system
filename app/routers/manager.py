from fastapi import Request, APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils.auth import get_current_user
from app.config import BASE_DIR

templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter(prefix="/manager")

@router.get("/", response_class=HTMLResponse)
def get_admin_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("manager.html", {"request": request})