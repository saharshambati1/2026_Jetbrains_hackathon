import requests
import os
from dotenv import load_dotenv

load_dotenv()

GRID_API_KEY = os.getenv("GRID_API_KEY")

headers = {
    "Authorization": f"Bearer {GRID_API_KEY}",
    "Content-Type": "application/json"
}

def get_match_data(match_id):
    url = f"https://api.grid.gg/matches/{match_id}"
    response = requests.get(url, headers=headers)
    return response.json()

# Example
data = get_match_data("2589176")
print(data)
