from fastapi.responses import JSONResponse
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware

from core.utils import verify_token


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        public_paths = [
            "/auth",
            "/docs",
        ]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        token = request.cookies.get("access_token")

        if not token:
            return JSONResponse(
                status_code=401, content={"detail": "Not authenticated"}
            )

        try:
            payload = verify_token(token)
            if not payload:
                return JSONResponse(
                    status_code=401, content={"detail": "Invalid or expired token"}
                )

            request.state.user = payload.get("auth_user")
        except JWTError:
            return JSONResponse(
                status_code=401, content={"detail": "Invalid or expired"}
            )

        response = await call_next(request)
        return response
