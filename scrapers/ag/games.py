import csv
import json
import os
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup

from scrapers.const import ENCODING
from scrapers.misc import get_url

COLUMNS = [
    "id",
    "name",
    "description",
    "playMode",
    "applicationCategory",
    "gamePlatform",
    "operatingSystem",
    "author",
    "publisher",
    "datePublished",
    "ratingValue",
    "ratingCount",
    "bestRating",
    "worstRating",
    "genre",
    "platform",
    "perspective",
    "control",
    "gameplay",
    "theme",
    "graphic_style",
    "presentation",
    "action_compulsory",
    "red_flags",
    "media",
]


def download_file(url: str, filepath: Path) -> None:
    if filepath.exists():
        return
    try:
        r = get_url(url)
    except requests.exceptions.RequestException as e:
        print(e)
        return
    if r.status_code != 200:
        print(f"error getting file: {url}")
        return
    with open(filepath, "wb") as f:
        f.write(r.content)
    sleep(0.5)


def download_cover(url: str, dest_dir: Path) -> None:
    filename = f"{url.rsplit('/', 2)[1]}.jpg"
    filepath = dest_dir / filename[0] / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    download_file(url, filepath)


def parse_html_file(html_file_path: Path, data_path: Path, scrape_covers: bool) -> dict:
    with open(html_file_path, "rb") as f:
        soup = BeautifulSoup(f, "html.parser")

    descr = dict.fromkeys(COLUMNS, None)

    descr["id"] = int(os.path.basename(html_file_path)[:-5])

    game_info = None
    data_scripts = soup.find_all("script", {"type": "application/ld+json"})
    for ds in data_scripts:
        ds_str = str(ds.string)
        if "VideoGame" in ds_str:
            try:
                game_info = json.loads(ds_str)
            except json.decoder.JSONDecodeError:
                print(f"error decoding json for: {html_file_path}")
                continue
            break
    if not game_info:
        print(f"game info not found: id={descr['id']}")
    else:
        for k, v in game_info.items():
            if k[0] == "@" or k == "url":
                continue
            if k not in descr and k not in ["aggregateRating"]:
                raise ValueError(f"new field: {k}")
            if k in ["author", "publisher"]:
                # few authors/publishers have brackets in their name, this conflicts with final CSV formatting
                descr[k] = [x.replace("[", "<").replace("]", ">") for x in v["name"]]
            elif k == "aggregateRating":
                for k_, v_ in v.items():
                    if k_[0] == "@" or k_ == "itemReviewed":
                        continue
                    if k_ not in descr:
                        raise ValueError(f"new field: {k_}")
                    descr[k_] = v_
            elif k == "datePublished" and v == "0":
                descr[k] = None
            else:
                descr[k] = v

    descr["name"] = soup.find("h1", {"class": "page_title"}).text

    game_desc_div = soup.find("div", {"id": "game_desc"})
    if game_desc_div:
        descr["description"] = game_desc_div.find("p").text

    if scrape_covers:
        cover_img = soup.find("img", {"id": "gamebox_new"})
        if cover_img:
            download_cover(cover_img["data-src"], data_path / "covers")

    div = soup.find("div", {"class": "our_verdict"})
    if div:
        div_ = div.find("div", {"itemprop": "reviewRating"})
        if div_:
            descr["ag_rating"] = float(div_.find("strong").text.split(" ")[0])
            div_ = div.find("div", {"class": "buy_product_new"})
            if div_:
                descr["store"] = [a["href"] for a in div_.find_all("a")]
        div = div.find("div", {"itemprop": "aggregateRating"})
        if div:
            descr["user_rating"] = float(div.find("span", {"itemprop": "ratingValue"}).text)
            descr["user_rating_count"] = float(div.find("span", {"itemprop": "reviewCount"}).text)

    div = soup.find("div", {"id": "comment-container"})

    div_ = div.find_all("div", {"class": "padding"})
    if div_ and len(div_) >= 2:
        descr["sys_requirements"] = div_[1].text

    tbl = div.find("table", {"class": "game_info_table"})
    for tr in tbl.find_all("tr"):
        tds = tr.find_all("td")
        field = tds[0].text.lower().replace(" ", "_").replace(")", "").replace("(", "")
        if field not in COLUMNS:
            print(f"addme: {field}")
            continue
        value = tds[1].text
        if value == "-":
            continue
        if "," in value:
            value = [x.strip() for x in value.split(",")]
        descr[field] = value
    return descr


def run(data_path: Path, scrape_covers: bool = False) -> None:
    res_file = data_path / "descr.csv"
    htmls_dir = data_path / "html"
    all_files = htmls_dir.rglob("*")
    all_html_files_count = len([f for f in htmls_dir.rglob("*") if f.suffix == ".html"])
    i = 1
    result = {}
    for file in all_files:
        if file.suffix != ".html":
            continue
        if i % 1000 == 1:
            print(f"processing file {file}: {i} of {all_html_files_count}")
        descr = parse_html_file(file, data_path, scrape_covers)
        if descr["id"] in result:
            print(f"duplicate entry found. id: {descr['id']}")
        else:
            result[descr["id"]] = descr
        i += 1
    try:
        with open(res_file, "w", encoding=ENCODING) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=COLUMNS)
            writer.writeheader()
            for _, descr in result.items():
                writer.writerow(descr)
    except IOError:
        print("I/O error")
