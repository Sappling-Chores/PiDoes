try:
    from paths import WALLPAPER_URLS_JSON
except ImportError:
    from APP.paths import WALLPAPER_URLS_JSON

load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")
BASE_URL = "https://api.unsplash.com"
date = datetime.now()
date, month , year = date.day, date.month, date.year
new_date = [year, month, date]

def fetch_data():
    if WALLPAPER_URLS_JSON.exists():
        with open(WALLPAPER_URLS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    return {}

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
    data = fetch_data()
    last_checked = data.get("last_checked")
    if new_date != last_checked:
        query_list = ["desktop-wallpaper", "nature", "japan", "space", "technology", "city-skyline", "3d-renders"]
        urls = get_urls(query_list, "landscape")
        print(urls)
        data["last_checked"] = new_date
        
        if "wallpapers" not in data or not isinstance(data["wallpapers"], dict):
            data["wallpapers"] = {}
        for query, url in zip(query_list, urls):
            data["wallpapers"][query] = url

        with open(WALLPAPER_URLS_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
    
if __name__ == "__main__":
    update_data()


