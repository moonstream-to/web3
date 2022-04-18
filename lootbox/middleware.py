import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from bugout.data import BugoutUser
from bugout.exceptions import BugoutResponseException
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .settings import bugout_client as bc

logger = logging.getLogger(__name__)


class DropperHTTPException(HTTPException):
    """
    Extended HTTPException to handle 500 Internal server errors
    and send crash reports.
    """

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        internal_error: Exception = None,
    ):
        super().__init__(status_code, detail, headers)
        if internal_error is not None:
            print(internal_error)
            # reporter.error_report(internal_error)


class BearerTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        request.state.token = None
        authorization_header = request.headers.get("authorization")
        if authorization_header is not None:
            user_token_list = authorization_header.split()
            if len(user_token_list) != 2:
                return Response(status_code=403, content="Wrong authorization header")
            user_token: str = user_token_list[-1]
            request.state.token = user_token
            return await call_next(request)
        elif request.method != "GET":
            return Response(status_code=403, content="No authorization header")

        return await call_next(request)
