import asyncio
import inspect
import logging
import threading

import httpx

from . import exceptions


logger = logging.getLogger(__name__)


class Auth(httpx.Auth):
    """
    Azimuth API authenticator.
    """
    def __init__(
        self,
        base_url,
        *,
        auth_data,
        authenticator = None,
        authenticator_type = None
    ):
        assert \
            authenticator or authenticator_type, \
            "one of authenticator or authenticator_type is required"
        self.base_url = base_url.rstrip("/")
        self.authenticator = authenticator
        self.authenticator_type = authenticator_type
        self.auth_data = auth_data
        self._token = None
        # We use locks to make sure only one request refreshes the token at once
        self._sync_lock = threading.RLock()
        self._async_lock = asyncio.Lock()

    def _raise_for_status(self, response):
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as source:
            raise exceptions.APIError(source)

    def _build_authenticators_request(self):
        logger.debug("building authenticators request")
        return httpx.Request("GET", f"{self.base_url}/auth/authenticators/")

    def _handle_authenticators_response(self, response):
        self._raise_for_status(response)
        try:
            authenticator = next(
                k
                for k, v in response.json().items()
                if v["type"] == self.authenticator_type
            )
        except StopIteration:
            raise exceptions.SDKError(f"no authenticators with type '{self.authenticator_type}'")
        else:
            logger.debug(
                f"using authenticator '{authenticator}' of type '{self.authenticator_type}'"
            )
            self.authenticator = authenticator

    def _build_token_request(self):
        logger.debug("building token refresh request")
        return httpx.Request(
            "POST",
            f"{self.base_url}/auth/{self.authenticator}/token/",
            json = self.auth_data
        )
    
    def _handle_token_response(self, response):
        self._raise_for_status(response)
        logger.debug("extracting token")
        self._token = response.json()["token"]

    def _authenticate_request(self, request):
        logger.debug("applying request authentication")
        request.headers["Authorization"] = f"Bearer {self._token}"
        return request
    
    def _refresh_token(self, lock):
        token = self._token
        yield lock.acquire()
        try:
            # If the token changed in the time it took to acquire the lock,
            # there is nothing to do
            if token != self._token:
                return
            if not self.authenticator:
                response = yield self._build_authenticators_request()
                self._handle_authenticators_response(response)
            response = yield self._build_token_request()
            self._handle_token_response(response)
        finally:
            lock.release()
    
    def auth_flow(self, request, lock):
        if not self._token:
            yield from self._refresh_token(lock)
        response = yield self._authenticate_request(request)
        if response.status_code == 401:
            # Try refreshing the token
            yield from self._refresh_token(lock)
            yield self._authenticate_request(request)

    def sync_auth_flow(self, request):
        flow = self.auth_flow(request, self._sync_lock)
        try:
            action = flow.send
            to_send = None
            while True:
                try:
                    yielded_obj = action(to_send)
                except StopIteration as exc:
                    break
                try:
                    if isinstance(yielded_obj, httpx.Request):
                        to_send = yield yielded_obj
                        to_send.read()
                    else:
                        to_send = yielded_obj
                except BaseException as exc:
                    action = flow.throw
                    to_send = exc
                else:
                    action = flow.send
        finally:
            flow.close()

    async def async_auth_flow(self, request):
        flow = self.auth_flow(request, self._async_lock)
        try:
            action = flow.send
            to_send = None
            while True:
                try:
                    yielded_obj = action(to_send)
                except StopIteration as exc:
                    break
                try:
                    if inspect.isawaitable(yielded_obj):
                        to_send = await yielded_obj
                    elif isinstance(yielded_obj, httpx.Request):
                        to_send = yield yielded_obj
                        await to_send.aread()
                    else:
                        to_send = yielded_obj
                except BaseException as exc:
                    action = flow.throw
                    to_send = exc
                else:
                    action = flow.send
        finally:
            flow.close()
