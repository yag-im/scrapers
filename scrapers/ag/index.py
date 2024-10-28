from pathlib import Path
from time import sleep

from bs4 import BeautifulSoup

from scrapers.ag.conf import DOMAIN
from scrapers.misc import get_url

SECTIONS = {"all", "freeware"}
SLEEP_OK = 0.5


def run(data_path: Path):
    """
    Fetch AG games index (all html pages of all games) and store into "data_path/html"
    """
    data_path.mkdir(parents=True, exist_ok=True)
    for s in SECTIONS:
        p = 152
        while True:
            url = f"{DOMAIN}/games/adventure/{s}-title-asc/page{p}"
            print(f"parsing index from page: {url}")
            res_idx_page = get_url(url)
            print(res_idx_page.content)
            soup = BeautifulSoup(res_idx_page.content, "html5lib")
            base_div = soup.find_all("div", {"class": "item_holder"})
            if len(base_div) < 2:
                print(f"finished processing section '{s}'")
                break  # no more games to process in this section
            cards = base_div[1].find_all("div", {"class": "card"})
            for h in cards:
                a = h.find("a")
                url = f"{DOMAIN}{a['href']}"
                url_parts = a["href"].split("/")
                game_prefix = url_parts[3]
                print(f"getting game page: {url}")
                game_page_html = get_url(url)
                html_files_folder = data_path / "html" / game_prefix[:1]
                html_files_folder.mkdir(parents=True, exist_ok=True)
                html_file_path = html_files_folder / (game_prefix + ".html")
                with open(html_file_path, "wb") as f:
                    f.write(game_page_html.content)
                sleep(SLEEP_OK)
            p += 1
