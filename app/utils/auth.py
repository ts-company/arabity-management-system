from fastapi import HTTPException, status
from jose import jwt, JWTError
from app.utils.jwt import SECRET_KEY, ALGORITHM


def get_current_user(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )