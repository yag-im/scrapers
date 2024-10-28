import typing as t

import requests
from requests import Response
from requests.adapters import (
    HTTPAdapter,
    Retry,
)

# requests
CONNECT_TIMEOUT = 3
READ_TIMEOUT = 120

# retry
TOTAL_ATTEMPTS = 5
BACKOFF_FACTOR = 3
ALLOWED_METHODS = ["GET", "POST"]
STATUS_FORCELIST = [429, 500, 502, 503, 504]


def __get_requests_session(
    total=TOTAL_ATTEMPTS,
    backoff_factor=BACKOFF_FACTOR,
    allowed_methods=ALLOWED_METHODS,
    status_forcelist=STATUS_FORCELIST,
):
    # backoff_factor = 3: 5, 10, 20, 40, 80, 160, 320, 640, 1280, 2560
    retries = Retry(
        total=total,
        backoff_factor=backoff_factor,
        allowed_methods=frozenset(allowed_methods),
        status_forcelist=status_forcelist,
    )
    sess = requests.Session()
    sess.mount("http://", HTTPAdapter(max_retries=retries))
    sess.mount("https://", HTTPAdapter(max_retries=retries))
    return sess


def get_url(url: str, params: t.Optional[dict] = None, headers: t.Optional[dict] = None) -> Response:
    s = __get_requests_session()
    return s.get(url, params=params, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))


def post_url(
    url: str, params: t.Optional[dict] = None, headers: t.Optional[dict] = None, data: t.Optional[str] = None
) -> Response:
    s = __get_requests_session()
    return s.post(url, params=params, headers=headers, data=data, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
