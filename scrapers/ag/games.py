import csv
import json
import os
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = f"{CUR_DIR}/../../data/ag"
HTML_DIR = f"{DATA_DIR}/html"
SCREENSHOTS_DIR = f"{DATA_DIR}/screenshots"
COVERS_DIR = f"{DATA_DIR}/covers"
RES_FILE = f"{DATA_DIR}/descr.csv"

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
]


def download_file(url, filepath):
    if os.path.exists(filepath):
        return
    try:
        r = requests.get(url)
    except Exception as e:
        print(e)
        return
    if r.status_code != 200:
        print(f"error getting file: {url}")
        return
    open(filepath, "wb").write(r.content)
    sleep(0.5)


def download_cover(url, dir):
    filename = f"{url.rsplit('/', 2)[1]}.jpg"
    filepath = os.path.join(dir, filename)
    download_file(url, filepath)


def parse_file(filepath):
    with open(filepath, "rb") as f:
        soup = BeautifulSoup(f, "html.parser")

    descr = dict.fromkeys(COLUMNS, None)

    descr["id"] = int(os.path.basename(filepath)[:-5])

    game_info = None
    data_scripts = soup.find_all("script", {"type": "application/ld+json"})
    for ds in data_scripts:
        ds_str = str(ds.string)
        if "VideoGame" in ds_str:
            game_info = json.loads(ds_str)
            break
    if not game_info:
        print(f"game info not found. id: {descr['id']}")
        return descr

    for k, v in game_info.items():
        if k[0] == "@" or k == "url":
            continue
        if k not in descr and k not in ["aggregateRating"]:
            raise Exception(f"new field: {k}")
        if k in ["author", "publisher"]:
            # few authors/publishers have brackets in their name, this conflicts with final CSV formatting
            descr[k] = [x.replace("[", "<").replace("]", ">") for x in v["name"]]
        elif k == "aggregateRating":
            for k_, v_ in v.items():
                if k_[0] == "@" or k_ == "itemReviewed":
                    continue
                if k_ not in descr:
                    raise Exception(f"new field: {k_}")
                descr[k_] = v_
        elif k == "datePublished" and v == "0":
            descr[k] = None
        else:
            descr[k] = v

    return descr

    """
    descr['name'] = soup.find("h1", {"class": "page_title"}).text

    cover_url = soup.find('div', {"class": "feat_image"})
    if cover_url:
        download_cover(cover_url.find('img')['data-src'], COVERS_DIR)

    description = soup.find('div', {"id": "game_desc"})
    if description:
        descr['description'] = description.text

    div = soup.find("div", {"class": "rblock_1"})
    developer = descr['developer'] = div.find('p', {"itemprop": "author"}).find('span')
    if developer:
        descr['developer'] = developer.text
    date_published = div.find('span', {"itemprop": "datePublished"})
    if date_published:
        parts = date_published.text.split('by')
        try:
            descr['date_published'] = dateutil.parser.parse(parts[0], fuzzy=True)
        except Exception as e:
            pass

    div = soup.find("div", {"class": "our_verdict"})
    if div:
        div_ = div.find('div', {"itemprop": "reviewRating"})
        if div_:
            descr['ag_rating'] = float(div_.find('strong').text.split(' ')[0])
            div_ = div.find('div', {"class": "buy_product_new"})
            if div_:
                descr['store'] = [a['href'] for a in div_.find_all('a')]
        div = div.find('div', {"itemprop": "aggregateRating"})
        if div:
            descr['user_rating'] = float(div.find('span', {"itemprop": "ratingValue"}).text)
            descr['user_rating_count'] = float(div.find('span', {"itemprop": "reviewCount"}).text)

    div = soup.find("div", {"id": "comment-container"})

    div_ = div.find_all("div", {"class": "padding"})
    if div_ and len(div_) >= 2:
        descr['sys_requirements'] = div_[1].text

    tbl = div.find("table", {"class": "game_info_table"})
    for tr in tbl.find_all("tr"):
        tds = tr.find_all("td")
        field = tds[0].text.lower().replace(' ', '_').replace(')', '').replace('(', '')
        if field not in COLUMNS:
            print(f'addme: {field}')
            continue
        value = tds[1].text
        if value == '-':
            continue
        if ',' in value:
            value = [x.strip() for x in value.split(',')]
        descr[field] = value
    return descr
    """


def run(data_path: Path):
    files = os.listdir(HTML_DIR)
    i = 1
    result = {}

    for filename in files:
        if i % 1000 == 1:
            print(f"processing file {filename}: {i} of {len(files)}")
        # filename = '16299.html'
        if not filename.endswith(".html"):
            continue
        # print(filename)
        descr = parse_file(os.path.join(HTML_DIR, filename))
        if descr["id"] in result:
            print(f"duplicate entry found. id: {descr['id']}")
        else:
            result[descr["id"]] = descr
        i += 1

    try:
        with open(RES_FILE, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=COLUMNS)
            writer.writeheader()
            for id, descr in result.items():
                writer.writerow(descr)
    except IOError:
        print("I/O error")
