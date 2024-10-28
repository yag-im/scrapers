import csv
import json
from pathlib import Path

from scrapers.igdb.misc import get_data

JSON_INDENT = 4

GENRE_ID_POINT_AND_CLICK = 2
GENRE_PUZZLE = 9
GENRE_ID_ADVENTURE = 31


def get_genres():
    return get_data("https://api.igdb.com/v4/genres", data="fields *;exclude checksum,url;sort id asc;")


def get_platforms():
    return get_data(
        "https://api.igdb.com/v4/platforms",
        data="fields *,platform_logo.image_id,versions.*,platform_family.name;exclude checksum,url;sort id asc;",
    )


def get_companies():
    return get_data(
        "https://api.igdb.com/v4/companies",
        data="fields *,logo.image_id,websites.url,websites.category;exclude developed,published,checksum,url;sort id asc;",
    )


def get_age_ratings():
    return get_data(
        "https://api.igdb.com/v4/age_ratings",
        data="fields rating,rating_cover_url;sort id asc;",
    )


def get_regions():
    return get_data(
        "https://api.igdb.com/v4/regions",
        data="fields *;sort id asc;",
    )


def get_games():
    res = []
    for genre in {GENRE_ID_ADVENTURE, GENRE_ID_POINT_AND_CLICK}:
        res += get_data(
            "https://api.igdb.com/v4/games",
            data=f"\
                fields\
                    *\
                    ,alternative_names.name\
                    ,bundles.name\
                    ,cover.image_id\
                    ,franchises.name\
                    ,game_modes.name\
                    ,genres.name\
                    ,involved_companies.*\
                    ,game_engines.name\
                    ,release_dates.human,release_dates.region\
                    ,age_ratings.category,age_ratings.rating,age_ratings.synopsis,age_ratings.content_descriptions.description\
                    ,screenshots.image_id,screenshots.height,screenshots.width\
                ;sort id asc;where genres={[genre]};",
        )
    return res


def get_game_by_id(id: int):
    return get_data(
        "https://api.igdb.com/v4/games",
        data=f"\
            fields\
                *\
                ,alternative_names.name\
                ,bundles.name\
                ,cover.image_id\
                ,franchises.name\
                ,game_modes.name\
                ,genres.name\
                ,involved_companies.*\
                ,game_engines.name\
                ,release_dates.human,release_dates.region\
                ,age_ratings.category,age_ratings.rating,age_ratings.synopsis,age_ratings.content_descriptions.description\
                ,screenshots.image_id,screenshots.height,screenshots.width\
            ;sort id asc;where id={id};",
    )


def run(data_path: Path) -> None:
    data_path.mkdir(parents=True, exist_ok=True)

    genres = get_genres()
    with open(data_path / "genres.json", "w") as f:
        json.dump(genres, f, indent=JSON_INDENT)

    fields_to_write = ["id", "name"]
    with open(data_path / "genres.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields_to_write)
        writer.writeheader()
        for i in genres:
            writer.writerow({field: i[field] for field in fields_to_write})

    platforms = get_platforms()
    with open(data_path / "platforms.json", "w") as f:
        json.dump(platforms, f, indent=JSON_INDENT)

    fields_to_write = ["id", "name", "abbreviation", "alternative_name", "slug"]
    with open(data_path / "platforms.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields_to_write)
        writer.writeheader()
        for i in platforms:
            writer.writerow({field: i.get(field, None) for field in fields_to_write})

    companies = get_companies()
    with open(data_path / "companies.json", "w") as f:
        json.dump(companies, f, indent=JSON_INDENT)

    fields_to_write = ["id", "name"]
    with open(data_path / "companies.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields_to_write)
        writer.writeheader()
        for i in companies:
            writer.writerow({field: i[field] for field in fields_to_write})

    games = get_games()
    with open(data_path / "games.json", "w") as f:
        json.dump(games, f, indent=JSON_INDENT)

    fields_to_write = [
        "name",
        "alternative_names",
        "short_descr",
        "long_descr",
        "genres",
        "companies",
        "platforms",
        "media_assets",
        "esrb_rating",
        "igdb",
    ]
    # with open(data_path / "games.json", "r") as ff:
    #    games = json.load(ff)
    with open(data_path / "games.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields_to_write, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writeheader()
        # there are duplicates because of how igdb handles genres parameter
        known_slugs = set()
        for i in games:
            # igdb
            if i["slug"] in known_slugs:
                continue
            igdb = json.dumps({"id": i["id"], "slug": i["slug"], "similar_ids": i.get("similar_games", None)})
            known_slugs.add(i["slug"])

            # alternative_names
            alternative_names = i.get("alternative_names", None)
            if alternative_names:
                alternative_names = (
                    "{" + ",".join(['"' + an["name"].replace('"', "") + '"' for an in alternative_names]) + "}"
                )

            # genres
            genres = "{" + ",".join([str(g["id"]) for g in i["genres"]]) + "}"

            # platforms
            platforms = i.get("platforms", None)
            if platforms:
                platforms = "{" + ",".join([str(p) for p in i["platforms"]]) + "}"

            # companies
            companies = i.get("involved_companies", None)
            if companies:
                companies = json.dumps(
                    [
                        {
                            "company": c["company"],
                            "developer": c["developer"],
                            "publisher": c["publisher"],
                            "porting": c["porting"],
                            "supporting": c["supporting"],
                        }
                        for c in companies
                    ]
                )

            # esrb_rating
            age_ratings = i.get("age_ratings", None)
            esrb_rating = None
            if age_ratings:
                for ar in age_ratings:
                    if ar["category"] == 1:
                        esrb_rating = ar["rating"]
                        break

            # media_assets
            screenshots = i.get("screenshots", None)
            if screenshots:
                screenshots = [
                    {
                        "height": s.get("height", None),
                        "width": s.get("width", None),
                        "image_id": s["image_id"],
                    }
                    for s in screenshots
                ]
            cover = {"image_id": i["cover"]["image_id"]} if "cover" in i else None
            media_assets = {"screenshots": screenshots, "cover": cover}
            media_assets = json.dumps(media_assets)

            writer.writerow(
                {
                    "name": i["name"],
                    "alternative_names": alternative_names,
                    "short_descr": i.get("summary", None),
                    "long_descr": i.get("storyline", None),
                    "genres": genres,
                    "companies": companies,
                    "platforms": platforms,
                    "media_assets": media_assets,
                    "esrb_rating": esrb_rating,
                    "igdb": igdb,
                }
            )
