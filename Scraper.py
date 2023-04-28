import time

import requests
from database import *


def scrape_record(username, my_id, availability_type):
    url = f"https://poshmark.com/vm-rest/users/{username}/posts/filtered"

    querystring = {
        "request": "{\"filters\":{\"department\":\"All\",\"inventory_status\":[\"availability_type\"]},\"query_and_facet_filters\":{\"creator_id\":\"username\"},\"experience\":\"all\",\"max_id\":my_id,\"count\":100}".replace(
            'username', username).replace('my_id', my_id).replace('availability_type', availability_type),
        "summarize": "true", "app_version": "2.55", "pm_version": "237.0.0"}

    payload = ""
    headers = {
        "authority": "poshmark.com",
        "accept": "application/json",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ur;q=0.7",
        "cookie": f"ps=%7B%22bid%22%3A%2264230c2fe67283e992f21efa%22%2C%22extvid%22%3A%22ext1%3A223a211a-f2bf-4483-a8c4-6b45d304f49b%22%7D; _csrf=uuTYKdI2i8hVSOC1UQc_7MJF; vsegv3=eyJsMDEiOiIwOTgiLCJsMDIiOiIxMjEiLCJsMDMiOiIwNjUiLCJsMDQiOiIwNzciLCJsMDUiOiIxMjgiLCJsMDYiOiIwNDMiLCJsMDciOiIwNjIiLCJsMDgiOiIwODYifQ%3D%3D; rt=%7B%22src%22%3A%5B%7B%22rf%22%3A%22%22%2C%22lpu%22%3A%22%2Fcloset%2F{username}%3Futm_source%26utm_content%3Dext_trk%253Dbranch%2526feature%253Dsh_cl_ss_ios%2526campaign%253Dshare_content_other_user__us.default.001%2526rfuid%253Dext1%253Aadf5571f-8c6b-4f53-9022-22c6288688e7%26br_t%3Dtrue%26_branch_match_id%3D1169289125428012244%26_branch_referrer%3DH4sIAAAAAAAAA8soKSkottLXL8gvztDLzdZP9c4zKynzSkqvTAIAILn1dhsAAAA%253D%22%2C%22lpt%22%3A%22Other%22%2C%22rs%22%3Anull%2C%22ca%22%3A%222023-03-28T15%3A48%3A05.964Z%22%7D%5D%7D; __ssid=38a0c779c02c5e21c0d59c2748fc0c0; _gcl_au=1.1.45196378.1680018488; FPC=e7e1443b-f3a3-459e-b3d9-ad1a17fd7c62; G_ENABLED_IDPS=google; _gid=GA1.2.352426275.1680018488; io_token_7c6a6574-f011-4c9a-abdd-9894a102ccef=mai5K20oop2GCqw4wVq+kyKDPilOyh+kZirvB/JkqBg=; _ga=GA1.1.1728920342.1680018488; _uetsid=ef782d30cd7f11ed963873bc38965689; _uetvid=ef785d10cd7f11eda3dcbbb7fdfbee2e; _scid=7e253c57-1cc8-4477-b448-13a302018306; _tt_enable_cookie=1; _ttp=RWzXYBHiEGsmgfL3pQeRsDH0yDy; _sctr=1|1679943600000; _gat_gtag_UA_24801737_5=1; tracker_device=d24b1aae-757c-4669-bdb2-494e55c85604; _ga_S34VRNNVTV=GS1.1.1680018488.1.1.1680020327.56.0.0; _dd_s=rum=0&expire=1680021259412",
        "pragma": "no-cache",
        "referer": f"https://poshmark.com/closet/{username}?availability=sold_out",

        "sec-ch-ua-mobile": "?0",

        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "x-xsrf-token": "M6t1NiQG-eOuOXJXGsWnZ5dapgm-nrDgAr0A"
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    # save response as json

    json_data = response.json()['data']

    if len(json_data) == 0:
        print("No data")
        return None

    json_ids = ["https://poshmark.com/listing/" + str(item.get('id', ' ')) for item in json_data]

    titles = [item.get('title', ' ') for item in json_data]
    descriptions = [item.get('description', ' ') for item in json_data]

    available_status = [item['inventory']['status'] for item in json_data]

    # brands list comprehension try except "" if no brand
    brands = []
    for item in json_data:
        try:
            if item['brand'] == None or item['brand'] == "" or item['brand'] == " ":
                brands.append("NA")
            else:
                brands.append(item['brand'])
        except:
            brands.append("NA")

    category = [item['catalog']['department_obj']['slug'] for item in json_data]

    prices = []
    for item in json_data:
        try:

            prices.append(item['price'])

        except:
            prices.append("NA")

    list_of_records = []
    max_id = get_max_row()
    for index in range(len(json_data)):
        already_done = get_file_data("Already_done.txt")
        if json_ids[index] in already_done:
            continue
        item_number = str(max_id + (index + 1))
        record = [item_number, titles[index], descriptions[index], available_status[index], brands[index],
                  category[index], str(float(prices[index])), "Poshmark", json_ids[index]]
        list_of_records.append(record)
        with open("Already_done.txt", 'a', encoding='utf-8') as file:
            file.write(json_ids[index] + '\n')

    # update to google sheets
    update_sheet(list_of_records)
    print("updated")


    return True


def get_file_data(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = file.read().strip().split('\n')
    return data


def scraper_function():
    users_details = ["smexyfun"]

    x = ['sold_out', 'available']
    for single_user in users_details:
        username = single_user
        for i in x:
            single_id = 1
            while True:
                print(f"Scraping {username} {single_id} {i}")
                try:
                    result = scrape_record(f"{username}", str(single_id), i)
                except Exception as e:
                    print(e)
                    print("Error scraping")
                    result = True

                if result is None:
                    break

                single_id += 1

scraper_function()
quit()





