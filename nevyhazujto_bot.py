import requests
import time
import config

known_items = set()

def get_new_items():
    url = "https://nevyhazujto.cz/get_items?category_id=2&limit=432&younger_24=true"
    
    items = requests.get(url).json()
    new_items = []
    
    for item in items:
        if item['item_location_id'] not in known_items:
            new_items.append(item)
            known_items.add(item['item_location_id'])
    
    new_items.reverse()
    
    return new_items


def format_item(item):
    return f"""
*{item['item_location_name']}*
{item['item_location_description']}
https://nevyhazujto.cz/#!/item/{item['item_location_id']}
""".strip()


def telegram_post(method, **params):
    for i in range(3):
        try:
            return requests.post("https://api.telegram.org/bot{}/{}".format(config.TELEGRAM_TOKEN, method), data=params).json()
        except Exception as ex:
            print("Failed to post to Telegram: {}: {}".format(type(ex), ex))
            time.sleep(1)


first_items = get_new_items()

while True:
    for item in get_new_items():
        print(format_item(item))
        telegram_post("sendMessage", text=format_item(item),
            chat_id=config.TELEGRAM_CHAT_ID, parse_mode="Markdown", disable_web_page_preview=True)
    print("Checked")
    time.sleep(30)
