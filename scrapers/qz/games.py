import csv
import datetime
import os
import re
from pathlib import Path
from time import sleep

import dateparser
import requests
from bs4 import BeautifulSoup

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = f"{CUR_DIR}/../../data/qz"
HTML_DIR = f"{DATA_DIR}/html"
SCREENSHOTS_DIR = f"{DATA_DIR}/screenshots"
COVERS_DIR = f"{DATA_DIR}/covers"
RES_FILE = f"{DATA_DIR}/descr.csv"

DOMAIN = "http://questzone.ru"

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


def download_file(url, dir):
    filename = url.rsplit("/", 1)[1]
    filepath = os.path.join(dir, filename)
    if os.path.exists(filepath):
        return
    try:
        r = requests.get(url)
    except Exception as e:
        print(url)
        print(e)
        return
    if r.status_code != 200:
        print(f"error getting file: {url}")
        return
    open(filepath, "wb").write(r.content)
    sleep(0.5)


def download_screenshots(url):
    dirpath = os.path.join(SCREENSHOTS_DIR, url.rsplit("/", 1)[1])
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    else:
        return
    try:
        r = requests.get(url)
    except Exception as e:
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


def parse_file(filepath):
    with open(filepath, "rb") as f:
        soup = BeautifulSoup(f.read().decode("cp1251"), "html5lib")

    tbl = soup.find("table", {"class": "txt"})

    descr = dict.fromkeys(COLUMNS, None)

    descr["id"] = int(Path(filepath).stem)
    descr["name"] = tbl.find("div", {"class": "hdr0"}).text

    rus_name = tbl.find("font")
    if rus_name and "/" not in rus_name.text:
        descr["rus_name"] = rus_name.text

    other_names = tbl.find("div", {"id": "names"})
    if other_names:
        descr["other_names"] = [x.strip().replace('"', "") for x in other_names.find("i").text.split("\n")]

    cover = tbl.find("img", {"alt": "Обложка"})
    if cover:
        # descr['cover'] = cover['src']
        # download_file(f"{DOMAIN}{cover['src']}", COVERS_DIR)
        pass

    for tr in tbl.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 1:
            if tds[0].find("div", {"align": "justify"}):
                descr["description"] = tds[0].text
            else:
                links = tds[0].find_all("a")
                if links:
                    link = links[-1]["href"][:-1]
                    if "questzone.ru/screenshots" in link:
                        pass
                        # download_screenshots(link)
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
                    print(filepath)
                    print(field)

    return descr


def run(data_path: Path):
    files = os.listdir(HTML_DIR)
    i = 1
    result = {}

    for filename in files:
        if i % 1000 == 1:
            print(f"processing file {filename}: {i} of {len(files)}")
        # filename = '507+eng.html'
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
