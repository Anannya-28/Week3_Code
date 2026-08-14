

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("online_shopping")


class AppError(Exception):
   
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


# ── FastAPI exception handlers (registered in main.py) ───────────────────────

def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
  
    logger.warning(
        "APP ERROR | %s %s | status=%s | detail=%s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


def unhandled_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    
    logger.error(
        "UNHANDLED ERROR | %s %s | error=%s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred", "status_code": 500},
    )
