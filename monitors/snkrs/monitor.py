from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

import requests as rq
import urllib3
from fp.fp import FreeProxy

from datetime import datetime
import time

import json
import logging
import traceback
import os

import locations

logging.basicConfig(filename='snkrs-monitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

enable_free_proxy_str = os.environ.get("ENABLE_FREE_PROXY", "False")
ENABLE_FREE_PROXY = enable_free_proxy_str.lower() == 'true'

free_proxy_location_str = os.environ.get("FREE_PROXY_LOCATION", '["GB"]')
try:
    FREE_PROXY_LOCATION = json.loads(free_proxy_location_str)
except json.JSONDecodeError:
    FREE_PROXY_LOCATION = ["GB"]

if ENABLE_FREE_PROXY:
    proxy_obj = FreeProxy(country_id=FREE_PROXY_LOCATION, rand=True)

INSTOCK =

def discord_webhook(title, description, url, thumbnail, price, style_code, sizes):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    webhook_url = os.environ.get("WEBHOOK")
    username = os.environ.get("USERNAME", "Nike SNKRS")
    avatar_url = os.environ.get("AVATAR_URL", "https://raw.githubusercontent.com/yasserqureshi1/Sneaker-Monitors/master/monitors/snkrs/logo.jpg")
    colour_str = os.environ.get("COLOUR", "16777215")
    try:
        colour = int(colour_str, 16)
    except ValueError:
        colour = 16777215

    data = {
        'username': username,
        'avatar_url':  avatar_url,
        'embeds': [{
            'title': title,
            'description': description,
            'url': url,
            'thumbnail': {'url': thumbnail},
            'color': colour,
            'footer': {'text': 'Developed by GitHub:yasserqureshi1'},
            'timestamp': str(datetime.utcnow()),
            'fields': [
                {'name': 'Price', 'value': price},
                {'name': 'Style Code', 'value': style_code},
                {'name': 'Sizes', 'value': sizes}
            ]
        }]
    }

    result = rq.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def monitor():
    """
    Initiates the monitor
    """
    print('''\n---------------------------------
--- SNKRS MONITOR HAS STARTED ---
---------------------------------\n''')
    logging.info(msg='Successfully started monitor')

    # Ensures that first scrape does not notify all products
    start = 1

    # Initialising proxy and headers
    proxy_list_str = os.environ.get("PROXY", '')
    try:
        PROXY = json.loads(proxy_list_str)
    except json.JSONDecodeError:
        PROXY =

    proxy_no = 0
    if ENABLE_FREE_PROXY:
        proxy = {'http': proxy_obj.get()}
    elif PROXY !=:
        proxy = {} if PROXY ==else {"http": PROXY[proxy_no], "https": PROXY[proxy_no]}
    else:
        proxy = {}
    user_agent = user_agent_rotator.get_random_user_agent()

    while True:
        # Makes request to site and stores products
        try:
            location = os.environ.get("LOCATION")
            language = os.environ.get("LANGUAGE")
            keywords_str = os.environ.get("KEYWORDS", '')
            try:
                KEYWORDS = json.loads(keywords_str)
            except json.JSONDecodeError:
                KEYWORDS =

            if location in locations.___standard_api___:
                to_discord = locations.standard_api(INSTOCK, location, language, user_agent, proxy, KEYWORDS, start)

            elif location == 'CL':
                to_discord = locations.chile(INSTOCK, location, language, user_agent, proxy, KEYWORDS, start)

            elif location == 'BR':
                to_discord = locations.brazil(INSTOCK, location, language, user_agent, proxy, KEYWORDS, start)

            else:
                print(f'LOCATION "{location}" CURRENTLY NOT AVAILABLE. IF YOU BELIEVE THIS IS A MISTAKE PLEASE CREATE AN ISSUE ON GITHUB OR MESSAGE THE #issues CHANNEL IN DISCORD.')
                return

            for product in to_discord:
                discord_webhook(product['title'], product['description'], product['url'], product['thumbnail'], product['price'], product['style_code'], product['sizes'])
                print(product['title'])

        except rq.exceptions.RequestException as e:
            logging.error(e)
            logging.info('Rotating headers and proxy')

            # Rotates headers
            user_agent = user_agent_rotator.get_random_user_agent()

            if ENABLE_FREE_PROXY:
                proxy = {'http': proxy_obj.get()}

            elif PROXY !=:
                proxy_no = 0 if proxy_no == (len(PROXY)-1) else proxy_no + 1
                proxy = {"http": PROXY[proxy_no], "https": PROXY[proxy_no]}

        except Exception as e:
            print(f"Exception found: {traceback.format_exc()}")
            logging.error(e)

        # Allows changes to be notified
        start = 0

        # User set delay
        delay_str = os.environ.get("DELAY", "5")
        try:
            delay = float(delay_str)
        except ValueError:
            print("Error: DELAY must be a number. Using default value 5.")
            delay = 5.0
        time.sleep(delay)

if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
