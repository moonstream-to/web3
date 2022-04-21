import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


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
