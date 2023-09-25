from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse


class CustomException(Exception):
    status_code = 500
    code = 0
    message = "Bad Request"

    def __init__(self, message: Optional[str] = None):
        if message:
            self.message = message


class ExistException(CustomException):
    message = "资源已存在"


class NoPermissionException(CustomException):
    status_code = 403
    message = "您没有此权限"


class NotFoundException(CustomException):
    status_code = 404
    message = "资源不存在"


class OverLimitException(CustomException):
    message = "资源超出限制"


async def error_exception_handler(_, exc: CustomException):
    content = {"code": exc.code, "detail": exc.message}
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


def register_exception(app: FastAPI):
    app.add_exception_handler(HTTPException, error_exception_handler)
    app.add_exception_handler(NotFoundException, error_exception_handler)
    app.add_exception_handler(ExistException, error_exception_handler)
    app.add_exception_handler(OverLimitException, error_exception_handler)
    app.add_exception_handler(NoPermissionException, error_exception_handler)
