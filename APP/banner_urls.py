from datetime import datetime
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")
BASE_URL = "https://api.unsplash.com"
date = datetime.now()
date, month , year = date.day, date.month, date.year
new_date = [year, month, date]

def fetch_data():
    json_file = "urls.json"
    with open(json_file, "r") as f:
        data = json.load(f)
    return data

def get_urls(query: list, orientation: str):
    old_date, old_month, old_year = 23, 8, 2026
    old_date = date if old_date < date else old_date
    print(old_date)
    url_list = []
    for i in query:
        url = f"{BASE_URL}/photos/random"
        headers = {"Authorization": f"Client-ID {ACCESS_KEY}"}
        params = {"orientation": orientation, "query": i}
        response = requests.get(url=url, headers=headers, params=params)
        data = response.json()
        url_list.append(data["urls"]["full"])
    return url_list

def update_data():
    json_file = "urls.json"
    data = fetch_data()
    last_checked = data["last_checked"]
    if new_date != last_checked:
        query_list = ["wallpaper", "nature", "japan", "landscape", "in-space", "technology"]
        urls = get_urls(query_list, "landscape")
        print(urls)
        updated_date = new_date
        data["last_checked"] = updated_date
        print(len(query_list))
        
        for query, url in zip(query_list, urls):
            data["urls"][0][query] = url

        with open(json_file, "w") as f:
            json.dump(data, f, indent=2)
        
    
if __name__ == "__main__":
    update_data()


