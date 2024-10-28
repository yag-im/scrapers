from pathlib import Path
from time import sleep

from bs4 import BeautifulSoup

from scrapers.misc import get_url
from scrapers.qz.conf import DOMAIN

INDEX_BASE_URL = f"{DOMAIN}/enzi/game"

LANGUAGES = {
    "eng": [chr(i) for i in range(ord("A"), ord("Z") + 1)] + ["0-9"],
    "rus": [chr(i) for i in range(ord("А"), ord("Я") + 1)],
}
SLEEP_OK = 0.5


def run(data_path: Path):
    data_path.mkdir(parents=True, exist_ok=True)
    for lang, letters in LANGUAGES.items():
        for letter in letters:
            url = f"{INDEX_BASE_URL}/letter_{lang}+{letter}"
            print(f"parsing index from page: {url}")
            res_idx_page = get_url(url)
            soup = BeautifulSoup(res_idx_page.content, "html.parser")
            for a in soup.find_all("div", {"class": "txt"})[1].find_all("a"):
                url_parts = a["href"].split("/")
                if len(url_parts) < 4:
                    continue
                game_prefix = url_parts[3]
                if "letter" in game_prefix:
                    continue
                url = f"{INDEX_BASE_URL}/{game_prefix}"
                print(f"getting game page: {url}")
                game_page_html = get_url(url)
                html_files_folder = data_path / "html" / game_prefix[:1]
                html_files_folder.mkdir(parents=True, exist_ok=True)
                html_file_path = html_files_folder / (game_prefix + ".html")
                with open(html_file_path, "wb") as f:
                    f.write(game_page_html.content)
                sleep(SLEEP_OK)
