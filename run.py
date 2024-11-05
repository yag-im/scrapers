import argparse
import os
from pathlib import Path

from scrapers.ag.games import run as ag_scrape_games
from scrapers.ag.index import run as ag_scrape_index
from scrapers.igdb.index import run as igdb_scrape_index
from scrapers.mg.index import run as mg_scrape_index
from scrapers.qz.games import run as qz_scrape_games
from scrapers.qz.index import run as qz_scrape_index

ENV_VAR_DATA_DIR = os.environ.get("DATA_DIR")
if ENV_VAR_DATA_DIR is None:
    raise ValueError("DATA_DIR env var is not set")
DATA_DIR = Path(ENV_VAR_DATA_DIR)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--target", type=str, choices=["ag", "igdb", "mg", "qz"], help="Specify the target website (ag, igdb, mg, qz)."
)
parser.add_argument("--index", action="store_true", help="Scrape index.")
parser.add_argument("--covers", action="store_true", help="Scrape covers.")
parser.add_argument("--screenshots", action="store_true", help="Scrape screenshots.")

args = parser.parse_args()
if args.target == "ag":
    if args.index:
        ag_scrape_index(DATA_DIR / "ag")
    ag_scrape_games(DATA_DIR / "ag", args.covers)
elif args.target == "igdb":
    if args.index:
        igdb_scrape_index(DATA_DIR / "igdb")
elif args.target == "mg":
    if args.index:
        mg_scrape_index(DATA_DIR / "mg")
elif args.target == "qz":
    if args.index:
        qz_scrape_index(DATA_DIR / "qz")
    qz_scrape_games(DATA_DIR / "qz", scrape_covers=args.covers, scrape_screenshots=args.screenshots)
