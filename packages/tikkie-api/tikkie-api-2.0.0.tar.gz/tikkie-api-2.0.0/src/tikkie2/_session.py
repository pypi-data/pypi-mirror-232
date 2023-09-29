import os
from functools import lru_cache
from typing import Any, Optional

import requests
from requests import Response

from tikkie2._version import VERSION
from tikkie2.errors import BaseError

API_KEY_ENV = "TIKKIE_API_KEY"
APP_TOKEN_ENV = "TIKKIE_APP_TOKEN"
API_URL_ENV = "TIKKIE_API_URL"
PRODUCTION_ENV = "TIKKIE_PRODUCTION"


class ApiSession(requests.Session):
    def __init__(
        self,
        *,
        api_key: str,
        app_token: Optional[str] = None,
        api_url: Optional[str] = None,
        production: bool = False,
    ):
        super().__init__()
        if api_url is None:
            api_url = "https://api.abnamro.com" if production else "https://api-sandbox.abnamro.com"

        self.api_url = api_url
        self.app_token = app_token
        self.api_key = api_key
        self.production = production

        self.headers["User-Agent"] = f"Python Tikkie API/{VERSION}"

    def prepare_request(self, request: Any) -> Any:
        request.url = "/".join(s.strip("/") for s in [self.api_url, "v2/tikkie", request.url])
        return super().prepare_request(request)

    def request(
        self,
        *args: Any,
        params: Any = None,
        app_token: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Response:
        dict_params = params or {}
        headers = kwargs.pop("headers", {})

        api_key = api_key or self.api_key
        app_token = app_token or self.app_token

        if not api_key:
            raise Exception("API Key is not set")

        if not app_token:
            raise Exception("App Token is not set")

        headers["API-Key"] = api_key
        headers["X-App-Token"] = app_token

        # Manually convert the json objects as we want to use a custom encoder
        # if "json" in kwargs:
        #     payload = kwargs.pop("json")
        #     kwargs["data"] = json.dumps(payload, cls=JSONEncoder)
        #     headers["Content-Type"] = "application/json"

        r = super().request(*args, params=dict_params, headers=headers, **kwargs)  # type: ignore
        if not r.ok:
            raise BaseError.from_response(r)
        return r


# The global session object
_session: Optional[ApiSession] = None


def _read_from_os(var: Optional[str], env: str) -> Optional[str]:
    if var is None:
        var = os.environ.get(env)
    return var


def _read_from_os_as_bool(var: Optional[bool], env: str) -> bool:
    if var is None:
        var = os.environ.get(env, "")
        return var.lower() in {"1", "on", "true", "yes"}
    return var


@lru_cache()
def get_session() -> ApiSession:
    global _session
    if _session is None:
        configure()
    return _session  # type: ignore


def configure(
    *,
    app_token: Optional[str] = None,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    production: Optional[bool] = True,
) -> None:
    global _session

    api_key = _read_from_os(api_key, API_KEY_ENV)
    app_token = _read_from_os(app_token, APP_TOKEN_ENV)
    api_url = _read_from_os(api_url, API_URL_ENV)
    production = _read_from_os_as_bool(production, PRODUCTION_ENV)

    get_session.cache_clear()

    _session = ApiSession(
        app_token=app_token, api_url=api_url, api_key=api_key, production=production
    )
