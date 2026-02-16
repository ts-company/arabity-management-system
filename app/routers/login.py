from fastapi import APIRouter, Form, Depends, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models.employees_model import Employee
from utils.password import verify_password
from utils.jwt import create_access_token
from database import get_db

router = APIRouter()

@router.post("/login")
async def login(username: str = Form(...),
                password: str = Form(...),
                db: Session = Depends(get_db)):
    user = db.query(Employee).filter(Employee.username == username).first()
    if not user or not verify_password(password, user.password):
        return RedirectResponse(url="/?error=1", status_code=status.HTTP_302_FOUND)
    token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    response = RedirectResponse(
        url=f"/{user.role}",
        status_code=status.HTTP_302_FOUND
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )

    return response

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
    )

    return {"message": "Logged out successfully"}
