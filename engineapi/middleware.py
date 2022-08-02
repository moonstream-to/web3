import base64
import json
import logging
from tracemalloc import start
from typing import Any, Awaitable, Callable, Dict, Optional

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from web3 import Web3

from .auth import (
    AUTH_PAYLOAD_NAME,
    DEFAULT_INTERVAL,
    MoonstreamAuthorization,
    MoonstreamAuthorizationExpired,
    MoonstreamAuthorizationVerificationError,
    authorize,
    verify,
)


logger = logging.getLogger(__name__)


class DropperAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, whitelist: Optional[Dict[str, str]] = None):
        self.whitelist: Dict[str, str] = {}
        if whitelist is not None:
            self.whitelist = whitelist
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        # Filter out endpoints with proper method to work without web3 autharization
        path = request.url.path.rstrip("/")
        method = request.method

        if path in self.whitelist.keys() and self.whitelist[path] == method:
            return await call_next(request)

        raw_authorization_header = request.headers.get("authorization")

        if raw_authorization_header is None:
            return Response(
                status_code=403, content="No authorization header passed with request"
            )

        authorization_header_components = raw_authorization_header.split()
        if (
            len(authorization_header_components) != 2
            or authorization_header_components[0].lower() != "moonstream"
        ):
            return Response(
                status_code=403,
                content="Incorrect format for authorization header. Expected 'Authorization: moonstream <base64_encoded_json_payload>'",
            )

        try:
            json_payload_str = base64.b64decode(
                authorization_header_components[-1]
            ).decode("utf-8")

            json_payload = json.loads(json_payload_str)
            verified = verify(json_payload)
            address = json_payload.get("address")
            if address is not None:
                address = Web3.toChecksumAddress(address)
            request.state.address = address
            request.state.verified = verified
        except MoonstreamAuthorizationVerificationError as e:
            logger.info("Moonstream authorization verification error: %s", e)
            return Response(status_code=403, content="Invalid authorization header")
        except MoonstreamAuthorizationExpired as e:
            logger.info("Moonstream authorization expired: %s", e)
            return Response(status_code=403, content="Authorization expired")
        except Exception as e:
            logger.info("Unexpected exception: %s", e)
            raise

        return await call_next(request)


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
