import json
from urllib.request import urlopen

URL = "https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json"

with urlopen(URL) as response:
    municipalities = json.load(response)

print(municipalities[0])
