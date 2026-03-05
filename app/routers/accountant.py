from fastapi import Request, APIRouter, HTTPException, status
from fastapi.templating import Jinja2Templates
from utils.auth import get_current_user

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/accountant")

@router.get("/")
def get_admin_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] !=  "accountant":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("accountant.html", {"request": request})