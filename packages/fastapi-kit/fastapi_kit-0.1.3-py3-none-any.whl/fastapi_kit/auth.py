from typing import Callable

from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, SimpleUser
from starlette.responses import JSONResponse

from .utils import decode_payload


class User(SimpleUser):
    def __init__(self, username: str, user_id: int) -> None:
        super().__init__(username)
        self.id = user_id

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            raise AuthenticationError('Invalid basic auth credentials')

        auth = conn.headers["Authorization"]
        permission = conn.headers.get('Permission', '')
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != 'bearer':
                raise AuthenticationError('Invalid basic auth credentials')
            payload_str = credentials.split('.')[1]
            payload = decode_payload(payload_str)
            permissions = permission.split()
        except Exception as exc:
            raise AuthenticationError('Invalid basic auth credentials')

        return (
            AuthCredentials(permissions),
            User(payload.username, payload.user_id)
        )


def on_auth_error(_, exc: Exception):
    return JSONResponse({"error": str(exc)}, status_code=401)


def register_auth(app: FastAPI, backend=None, on_error: Callable = on_auth_error):
    if backend is None:
        backend = BasicAuthBackend()
    app.add_middleware(
        AuthenticationMiddleware,
        backend=backend,
        on_error=on_error
    )
