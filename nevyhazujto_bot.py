import time
import config

import requests
from bs4 import BeautifulSoup

class Site(): pass

class Nevyhazujto(Site):
    def __init__(self):
        self.known_items = set()

    def get_new_items(self):
        url = "https://nevyhazujto.cz/get_items?category_id=2&limit=432&younger_24=true"
        
        items = requests.get(url).json()
        new_items = []
        
        for item in items:
            if item['item_location_id'] not in self.known_items:
                new_items.append(item)
                self.known_items.add(item['item_location_id'])
        
        new_items.reverse()
        
        return new_items


    def format_item(self, item):
        print(item)
        return """
*{0[item_location_name]}*
{0[item_location_description]}
_{0[region_name]}_
https://nevyhazujto.cz/#!/item/{0[item_location_id]}
""".format(item).strip()

class Item():
    pass

class Vsezaodvoz(Site):
    def __init__(self):
        self.known_items = set()
    
    def get_new_items(self):
        url = "https://vsezaodvoz.cz/inzeraty/elektro"
        
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        
        new_items = []
        
        for item_div in soup.find_all("div", class_="product-inline-item"):
            item_id = int(item_div['data-id'])
            if item_id not in self.known_items:
                item = Item()
                item.title = item_div.find("h3").a.text.strip()
                item.url = item_div.find("h3").a['href']
                item.description = list(item_div.find(class_="product-inline-content").children)[-1].string.strip()
                item.labels = [x.text.strip() for x in item_div.find(class_="product-inline-content").find_all(class_='product-label')]
                item.location = item_div.find(class_="product-inline-bottom-left").text.strip()
                
                self.known_items.add(item_id)
                if "daruji" not in item.labels:
                    continue
                new_items.append(item)
        
        new_items.reverse()
        
        return new_items

    def format_item(self, item):
        return """
*{0.title}*
{0.description}
_{0.location}_
https://vsezaodvoz.cz/{0.url}
""".format(item).strip()


def telegram_post(method, **params):
    for i in range(3):
        try:
            return requests.post("https://api.telegram.org/bot{}/{}".format(config.TELEGRAM_TOKEN, method), data=params).json()
        except Exception as ex:
            print("Failed to post to Telegram: {}: {}".format(type(ex), ex))
            time.sleep(1)

sites = [Nevyhazujto(), Vsezaodvoz()]

for site in sites:
    first = site.get_new_items()
    #print(site.format_item(first[0]))
 
while True:
    for site in sites:
        for item in site.get_new_items():
            print(site.format_item(item))
            telegram_post("sendMessage", text=site.format_item(item),
                chat_id=config.TELEGRAM_CHAT_ID, parse_mode="Markdown", disable_web_page_preview=True)
        print("Checked {}".format(type(site).__name__))
    time.sleep(30)
