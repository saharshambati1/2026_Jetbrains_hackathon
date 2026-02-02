import requests
import os
from dotenv import load_dotenv
import json


load_dotenv()

GRID_API_KEY = os.getenv("GRID_API_KEY")

headers = {
    "x-api-key": GRID_API_KEY
}

response = requests.get(
    "https://api.grid.gg/file-download/end-state/grid/series/2589176",
#   "https://api.grid.gg/products",
    headers=headers
)
print(response.status_code)
print(response.text)

