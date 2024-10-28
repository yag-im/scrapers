import json
import time
import typing as t
from pathlib import Path

from scrapers.mg.secrets import API_KEY
from scrapers.misc import get_url

MIN_SLEEP = 10
JSON_INDENT = 4

GENRE_ADVENTURE = 2
FORMAT_NORMAL = "normal"


def __get_url(url: str, params: t.Optional[dict] = None):
    if not params:
        params = {}
    params["api_key"] = API_KEY
    return get_url(url, params=params)


def get_genres():
    return __get_url("https://api.mobygames.com/v1/genres").json()["genres"]


def get_groups():
    res_groups = []
    offset = 0
    limit = 100
    while True:
        groups = __get_url("https://api.mobygames.com/v1/groups", params={"limit": limit, "offset": offset})
        groups_ = groups.json()["groups"]
        if not groups_:
            break
        res_groups += groups_
        offset += limit
        time.sleep(MIN_SLEEP)
    return res_groups


def get_games():
    res_games = []
    offset = 0
    limit = 100
    while True:
        games = __get_url(
            "https://api.mobygames.com/v1/games",
            params={"limit": limit, "offset": offset, "genre": GENRE_ADVENTURE, "format": FORMAT_NORMAL},
        )
        games_ = games.json()["games"]
        if not games_:
            break
        res_games += games_
        offset += limit
        time.sleep(MIN_SLEEP)
    return res_games


def get_platforms():
    return __get_url("https://api.mobygames.com/v1/platforms").json()["platforms"]


def run(data_path: Path) -> None:
    data_path.mkdir(parents=True, exist_ok=True)
    """
    genres = get_genres()
    with open(data_path / "genres.json", "w") as f:
        json.dump(genres, f, indent=JSON_INDENT)
    time.sleep(MIN_SLEEP)
    groups = get_groups()
    with open(data_path / "groups.json", "w") as f:
        json.dump(groups, f, indent=JSON_INDENT)
    time.sleep(MIN_SLEEP)
    platforms = get_platforms()
    with open(data_path / "platforms.json", "w") as f:
        json.dump(platforms, f, indent=JSON_INDENT)
    """
    games = get_games()
    with open(data_path / "games.json", "w") as f:
        json.dump(games, f, indent=JSON_INDENT)
