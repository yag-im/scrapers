import requests

API_BASE_URL = "https://api.rawg.io/api/"

params = {"page_size": 20}  # seems that's max
r = requests.get(API_BASE_URL + "games", params=params, timeout=(3, 30))
res_raw = r.json()

a = 1
