import csv
import datetime
import os
import re
from pathlib import Path
from time import sleep

import dateparser
import requests
from bs4 import BeautifulSoup

from scrapers.misc import get_url
from scrapers.qz.conf import DOMAIN

COLUMNS = [
    "id",
    "name",
    "rus_name",
    "other_names",
    "description",
    "website",
    "developer",
    "publisher",
    "date_published",
    "lang",
    "other_lang",
    "platform",
    "genre",
    "view",
    "control",
    "media",
    "license",
    "sys_requirements",
    "engine",
    "emulator",
    "novel",
    "project_status",
    "store_link",
]
ENCODING = "UTF-16"


def download_file(url: str, output_dir: Path) -> None:
    filename = url.rsplit("/", 1)[1]
    filepath = output_dir / filename
    if filepath.exists():
        return
    try:
        r = get_url(url)
    except requests.exceptions.RequestException as e:
        print(url)
        print(e)
        return
    if r.status_code != 200:
        print(f"error getting file: {url}")
        return
    with open(filepath, "wb", encoding=ENCODING) as f:
        f.write(r.content)
    sleep(0.5)


def download_screenshots(url: str, data_path: Path) -> None:
    dirpath = data_path / "screenshots" / url.rsplit("/", 1)[1]
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    else:
        return
    try:
        r = get_url(url)
    except requests.exceptions.RequestException as e:
        print(url)
        print(e)
        return
    if r.status_code != 200:
        print(f"error getting page: {url}")
        return
    soup = BeautifulSoup(r.content, "html5lib")
    tbl = soup.find("table")
    for img in tbl.find_all("img"):
        if "/screenshots/" in img["src"]:
            url_path = img["src"].strip()
            url_path = url_path.replace("_s.jpg", ".jpg")
            download_file(f"{DOMAIN}{url_path}", dirpath)


def parse_html_file(html_file_path: Path, data_path: Path, scrape_covers: bool, scrape_screenshots: bool) -> dict:
    with open(html_file_path, "rb") as f:
        soup = BeautifulSoup(f.read().decode("cp1251"), "html5lib")

    tbl = soup.find("table", {"class": "txt"})

    descr = dict.fromkeys(COLUMNS, None)

    descr["id"] = int(html_file_path.stem)
    descr["name"] = tbl.find("div", {"class": "hdr0"}).text

    rus_name = tbl.find("font")
    if rus_name and "/" not in rus_name.text:
        descr["rus_name"] = rus_name.text

    other_names = tbl.find("div", {"id": "names"})
    if other_names:
        descr["other_names"] = [x.strip().replace('"', "") for x in other_names.find("i").text.split("\n")]

    if scrape_covers:
        cover = tbl.find("img", {"alt": "Обложка"})
        if cover:
            descr["cover"] = cover["src"]
            download_file(f"{DOMAIN}{cover['src']}", data_path / "covers")
            pass

    for tr in tbl.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 1:
            if tds[0].find("div", {"align": "justify"}):
                descr["description"] = tds[0].text
            else:
                if scrape_screenshots:
                    links = tds[0].find_all("a")
                    if links:
                        link = links[-1]["href"][:-1]
                        if "questzone.ru/screenshots" in link:
                            download_screenshots(link, data_path)
        elif len(tds) >= 2:
            field = tds[0].text
            value = tds[1].text
            if "Сайт(ы) игры" in field:
                descr["website"] = [a["href"] for a in tds[1].find_all("a")]
            elif "Разработка" in field:
                descr["developer"] = [x.strip() for x in value.split("/") if x != "-"]
            elif "Издание" in field:
                descr["publisher"] = value
            elif "Вышла:" in field or "Дата выхода" in field or "Выйдет:" in field:
                date_published = dateparser.parse(value, languages=["ru"], settings={"TIMEZONE": "UTC"})
                if not date_published:
                    # try to handle cases like "в ноябре 2005", find year and make up a date
                    match = re.match(r".*([1-3][0-9]{3})", value)
                    if match is not None:
                        date_published = datetime.datetime(int(match.group(1)), 1, 1, 0, 0, 0)
                descr["date_published"] = date_published
            elif "Язык" in field:
                descr["lang"] = value
            elif "Другие" in field:
                descr["other_lang"] = [x.strip() for x in value.split("/") if x.strip() != "-"]
            elif "Платформы" in field:
                platform = tds[1].find("b")
                if platform:
                    descr["platform"] = platform.text
                else:
                    descr["platform"] = value
            elif "Жанры" in field:
                descr["genre"] = [x.strip() for x in value.split("/") if x != "-"]
            elif "Вид" in field:
                descr["view"] = value.strip()
            elif "Управление" in field:
                if value != "-":
                    descr["control"] = value
            elif "Носитель" in field:
                descr["media"] = [x.strip() for x in value.split("/") if x != "-"]
            elif "Лицензия" in field:
                descr["license"] = value
            elif "Системные требования" in field:
                descr["sys_requirements"] = value
            elif "Движок" in field:
                descr["engine"] = value.strip()
            elif "Можно запустить" in field:
                descr["emulator"] = value
            elif "Новеллы" in field:
                descr["novel"] = value
            elif "Проект" in field:
                descr["project_status"] = value
            elif "Купить" in field:
                store_link = tds[1].find("a")
                if store_link:
                    descr["store_link"] = store_link["href"]
            else:
                if (
                    "Обзоры" not in field
                    and "Тип локализации" not in field
                    and "Прохождения" not in field
                    and "Переводы" not in field
                    and "Ролики" not in field
                    and "Скачать" not in field
                    and "России" not in field
                    and "Локализация" not in field
                    and "Создатели поимённо" not in field
                    and "Российская поставка" not in field
                    and "Российская дата" not in field
                    and "<<" not in field
                    and ">>" not in field
                    and ": " != field
                    and ":" != field
                ):
                    print(html_file_path)
                    print(field)

    return descr


def run(data_path: Path, scrape_covers: bool = False, scrape_screenshots: bool = False) -> None:
    html_dir = data_path / "html"
    res_file = data_path / "descr.csv"
    files = os.listdir(html_dir)
    i = 1
    result = {}

    for filename in files:
        if i % 1000 == 1:
            print(f"processing file {filename}: {i} of {len(files)}")
        # filename = '507+eng.html'
        if not filename.endswith(".html"):
            continue
        # print(filename)
        descr = parse_html_file(html_dir / filename, data_path, scrape_covers, scrape_screenshots)
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
