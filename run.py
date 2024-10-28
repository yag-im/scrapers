from pathlib import Path

# from scrapers.ag.games import run as ag_parse_index
# from scrapers.ag.index import run as ag_scrape_index
# from scrapers.igdb.index import get_game_by_id
from scrapers.igdb.index import run as igdb_scrape_index

# from scrapers.mg.index import run as mg_scrape_index
# from scrapers.qz.games import run as qz_parse_index
# from scrapers.qz.index import run as qz_scrape_index

# qz_scrape_index(Path("data/qz"))
# ag_scrape_index(Path("data/ag"))
# mg_scrape_index(Path("data/mg"))
igdb_scrape_index(Path("data/igdb"))
# res = get_game_by_id(149734)
a = 1
