import json
import os
import time
import typing as t
from pathlib import Path

import requests

from scrapers.const import ENCODING
from scrapers.misc import get_url

API_KEY = os.environ.get("MOBYGAMES_API_KEY")

MIN_SLEEP = 10
JSON_INDENT = 4

HOST_URL = "https://api.mobygames.com/v1"
GENRE_ADVENTURE = 2
FORMAT_NORMAL = "normal"


def _get_url(url: str, params: t.Optional[dict] = None) -> requests.Response:
    if not params:
        params = {}
    params["api_key"] = API_KEY
    return get_url(url, params=params)


def get_genres() -> list:
    return _get_url(f"{HOST_URL}/genres").json()["genres"]


def get_groups() -> list:
    res_groups = []
    offset = 0
    limit = 100
    while True:
        groups = _get_url(f"{HOST_URL}/groups", params={"limit": limit, "offset": offset})
        groups_ = groups.json()["groups"]
        if not groups_:
            break
        res_groups += groups_
        offset += limit
        time.sleep(MIN_SLEEP)
    return res_groups


def get_games() -> list:
    res_games = []
    offset = 0
    limit = 100
    while True:
        games = _get_url(
            f"{HOST_URL}/games",
            params={"limit": limit, "offset": offset, "genre": GENRE_ADVENTURE, "format": FORMAT_NORMAL},
        )
        games_ = games.json()["games"]
        if not games_:
            break
        res_games += games_
        offset += limit
        time.sleep(MIN_SLEEP)
    return res_games


def get_platforms() -> list:
    return _get_url(f"{HOST_URL}/platforms").json()["platforms"]


def run(data_path: Path) -> None:
    data_path.mkdir(parents=True, exist_ok=True)
    genres = get_genres()
    with open(data_path / "genres.json", "w", encoding=ENCODING) as f:
        json.dump(genres, f, indent=JSON_INDENT)
    time.sleep(MIN_SLEEP)
    groups = get_groups()
    with open(data_path / "groups.json", "w", encoding=ENCODING) as f:
        json.dump(groups, f, indent=JSON_INDENT)
    time.sleep(MIN_SLEEP)
    platforms = get_platforms()
    with open(data_path / "platforms.json", "w", encoding=ENCODING) as f:
        json.dump(platforms, f, indent=JSON_INDENT)
    games = get_games()
    with open(data_path / "games.json", "w", encoding=ENCODING) as f:
        json.dump(games, f, indent=JSON_INDENT)
