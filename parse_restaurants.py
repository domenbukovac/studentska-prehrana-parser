from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from time import sleep
import psycopg2

from decimal import Decimal
import json
import os

dirname = os.path.dirname(__file__)
config_file = os.path.join(dirname, 'config.json')


with open(config_file) as json_data_file:
    database = json.load(json_data_file)["DATABASE"]
print(database["user"])


url = "https://www.studentska-prehrana.si/restaurant/"

uClient = uReq(url)
page_html = uClient.read()
uClient.close()

page_soup = soup(page_html, "html.parser")
restavracije = page_soup.findAll(
    'div', attrs={
        'class': 'restaurant-row'
    })


try:
    connect_str = f"dbname='{database['db_name']}' user='{database['user']}' host='{database['host']}' password='{database['password']}'"
    conn = psycopg2.connect(connect_str)
    cursor = conn.cursor()

    query = """INSERT INTO restaurants_sp 
        (name, sp_id, street, zip, city, students_meal_price, latitude, longitude) 
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s);"""

    tag_query = """INSERT INTO restaurant_tags 
        (restaurant_sp_id, name) 
        VALUES
        (%s, %s);"""
except Exception as e:
    print(e)

vsi_atributi = []
unikatni_atributi = []

for restavracija in restavracije:

  name =  restavracija.a.text.strip()
  latitude = Decimal(restavracija.attrs['data-lat'])
  longitude = Decimal(restavracija.attrs['data-lon'])
  meal_price = Decimal(restavracija.attrs['data-doplacilo'].replace(",", "."))
  sp_id =  restavracija.attrs['data-posid']
  address = restavracija.attrs['data-naslov']
  city = restavracija.attrs['data-city']

  naslov = restavracija.small.i.text.split(", ")
  kraj = naslov[1].split(" ")
  zip = kraj[0]

  print("Name: " + name)
  print("Koordinates: " + str(longitude), str(latitude))
  print("Bon: " + str(meal_price))
  print("Id: " + sp_id)
  print("Address: " + address)
  print("City: " + city)

  atributi = restavracija.find(
    'div', attrs={
        'class': 'pull-right'
    })
  slike = atributi.findAll('img')


  data = (name, sp_id, address, zip, city, meal_price, latitude, longitude)
  cursor.execute(query, data)
  conn.commit()

  for atribut in slike:
    tag_name = atribut['title']

    tag_data = (sp_id, tag_name)
    cursor.execute(tag_query, tag_data)
    conn.commit()

  print("\n\n")
