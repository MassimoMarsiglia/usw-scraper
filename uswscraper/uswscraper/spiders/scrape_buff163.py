import requests
from dotenv import load_dotenv
from uswscraper.uswscraper.database.database import DatabaseManager
from uswscraper.uswscraper.models.Buff163 import Buff163_Listing
import json

def scrape_buff163_listings():
    url = "https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=36338&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1749772147804"
    response = requests.get(url)
    data = response.json()

    if data["code"] != "OK":
        print("Error fetching data")
        return

    items = data["data"]["items"]

    db = DatabaseManager()
    db.connect()
    session = db.get_session()

    print(json.dumps(items[0], indent=2))

    for item in items:
        if "id" not in item or "asset_info" not in item:
            print("Skipping item due to missing keys:", item)
            continue

        skin_variant_id = str(item["id"])
        item_name = item.get("description") or item["asset_info"].get("description") or f"Item {item['id']}"
        request_data = json.loads(json.dumps(item))

        listing = Buff163_Listing(
            skin_variant_id=skin_variant_id,
            item_name=item_name,
            request_data=request_data
        )
        session.add(listing)


    session.commit()
    session.close()
    print("Total inserted listings:", session.query(Buff163_Listing).count())
    print(f"Saved {len(items)} listings.")

if __name__ == "__main__":
    load_dotenv()
    scrape_buff163_listings()