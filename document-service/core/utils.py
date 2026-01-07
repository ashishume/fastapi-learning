import os
from fastapi import HTTPException, Request
from jose import JWTError, jwt


SECRET_KEY = os.getenv("TOKEN_SECRET", "admin1234@")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"




def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def auth_guard(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authorised")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    request.state.user = payload.get("auth_user")
    request.state.user_id = str(payload.get("auth_user_id"))
    return payload.get("auth_user"), str(payload.get("auth_user_id"))
