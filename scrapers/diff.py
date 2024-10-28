import csv
import re

QZ_DESCR_DB_PATH = "../data/qz/descr.csv"
AG_DESCR_DB_PATH = "../data/ag/descr.csv"
MISSING_PATH = "../data/qz_missing.csv"
MATCHING_PATH = "../data/qz_matching.csv"
TARGET_SIMILARITY = 0.55

COLUMNS_AG = [
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


def find_ngrams(text: str, number: int = 3) -> set:
    """
    returns a set of ngrams for the given string
    :param text: the string to find ngrams for
    :param number: the length the ngrams should be. defaults to 3 (trigrams)
    :return: set of ngram strings
    """

    if not text:
        return set()

    words = [f"  {x} " for x in re.split(r"\W+", text.lower()) if x.strip()]

    ngrams = set()

    for word in words:
        for x in range(0, len(word) - number + 1):
            ngrams.add(word[x : x + number])

    return ngrams


def similarity(text1: str, text2: str, number: int = 3) -> float:
    """
    Finds the similarity between 2 strings using ngrams.
    0 being completely different strings, and 1 being equal strings
    """

    ngrams1 = find_ngrams(text1, number)
    ngrams2 = find_ngrams(text2, number)

    num_unique = len(ngrams1 | ngrams2)
    num_equal = len(ngrams1 & ngrams2)

    if num_unique == 0:
        print(text1, text2)

    return (float(num_equal) / float(num_unique)) if num_unique else 0


def ts_similarity(ts1, ts2, days_diff):
    return abs((ts1 - ts2).days) < days_diff


def find_similar_games(descr, db):
    res = []
    for k, v in db.items():
        sim = similarity(descr["name"], v["name"])
        if sim >= TARGET_SIMILARITY:
            res.append((sim, v))
            # do not break here, there might be better matches further in db
        elif v["other_names"]:
            for othn in v["other_names"].split(","):
                sim = similarity(descr["name"], othn)
                if sim >= TARGET_SIMILARITY:
                    res.append((sim, v))
                    break
    if not res:  # no similarities found
        return None
    elif len(res) > 1:
        # find the best match among many
        res.sort(key=lambda x: (x[0]), reverse=True)
    return res[0]


with open(QZ_DESCR_DB_PATH, mode="r") as f:
    csv_reader = csv.DictReader(f)
    qz_db = {row["id"]: row for row in csv_reader}

with open(AG_DESCR_DB_PATH, mode="r") as f:
    csv_reader = csv.DictReader(f)
    ag_db = {row["id"]: row for row in csv_reader}

misses = []
matches = []
manual = []
i = 0

# trying to find games present in AG, but absent in QZ
for _, v in ag_db.items():
    print(f'{i} processing: {v["name"]}')
    sim = find_similar_games(v, qz_db)
    if sim is None:
        misses.append(v)
        print("\t\tmissing")
    else:
        matches.append((v, sim))
        print("\t\tmatching")
    i += 1

print(f"missing: {len(misses)}")
print(f"matches: {len(matches)}")
print(f"manual: {len(manual)}")


with open(MISSING_PATH, "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=COLUMNS_AG)
    writer.writeheader()
    for el in misses:
        writer.writerow(el)


with open(MATCHING_PATH, "w") as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=[
            "id_ag",
            "name_ag",
            "date_ag",
            "author_ag",
            "publisher_ag",
            "similarity",
            "id_qz",
            "name_qz",
            "date_qz",
            "author_qz",
            "publisher_qz",
        ],
    )
    writer.writeheader()
    for el in matches:
        writer.writerow(
            {
                "id_ag": el[0]["id"],
                "name_ag": el[0]["name"],
                "date_ag": el[0]["datePublished"],
                "author_ag": el[0]["author"],
                "publisher_ag": el[0]["publisher"],
                "similarity": el[1][0],
                "id_qz": el[1][1]["id"],
                "name_qz": el[1][1]["name"],
                "date_qz": el[1][1]["date_published"],
                "author_qz": el[1][1]["developer"],
                "publisher_qz": el[1][1]["publisher"],
            }
        )
