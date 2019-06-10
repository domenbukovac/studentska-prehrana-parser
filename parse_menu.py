from bs4 import BeautifulSoup as soup
from time import sleep
import psycopg2
import requests
import datetime
import json

import os

dirname = os.path.dirname(__file__)
config_file = os.path.join(dirname, 'config.json')

# load database config from config
with open(config_file) as json_data_file:
    database = json.load(json_data_file)["DATABASE"]

try: # database config
    connect_str = f"dbname='{database['db_name']}' user='{database['user']}' host='{database['host']}' port='{database['port']}' password='{database['password']}'"
    conn = psycopg2.connect(connect_str)
    cursor = conn.cursor()
except Exception as e:
    print(e)

# request url
url = "https://www.studentska-prehrana.si/sl/restaurant/MenuForDate"
today = datetime.date.today()
query = """INSERT INTO daily_menus_sp 
        (restaurant_sp_id, title, tag, description, date) 
        VALUES
        (%s, %s, %s, %s, %s);"""


cursor.execute("""SELECT sp_id, name FROM restaurants_sp""")
weekday = today.weekday()

# days left this week
# days_to_check =  7 - weekday
days_to_check = 8

# every restaurant id in database
for restaurant in cursor.fetchall():
    # rande of days
    for i in range (0, days_to_check):
        date = today + datetime.timedelta(days=i)
        restaurant_sp_id = restaurant[0]

        # check if any menu already exists on selected day for this restaurant
        query2 = "SELECT id FROM daily_menus_sp WHERE date::date = '{}' AND restaurant_sp_id = {}".format(date, restaurant_sp_id)
        cursor.execute(query2)


        if (len(cursor.fetchmany(2)) == 0):
            res = requests.post(url, data={'restaurantId': restaurant_sp_id, 'date': date})

            page_html = res.text
            page_soup = soup(page_html, "html.parser")

            menus = page_soup.findAll(
                'div', attrs={
                    'class': 'shadow-wrapper'
                })

            for menu in menus:
                title = menu.h5.strong.text.split("  ")[1].replace('\t', '').capitalize()
                tag = None
                try:
                    tag = menu.find("img", attrs={"class" : "pull-right"}).attrs['title']
                except:
                    None
                description = []

                description_elements = menu.findAll("li")

                for element in description_elements:
                    description.append(element.i.text.replace('\t', ''))
                
                description_string = "\n".join(description)
                print(title)
                print(description_string)
                print(tag)
                print("\n")
                
                data = (restaurant_sp_id, title, tag, description_string, date)
                cursor.execute(query, data)
                conn.commit()
        else:
            print("Already exists")