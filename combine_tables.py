import psycopg2
import json
import sys

# load database config from config
with open('config.json') as json_data_file:
    database = json.load(json_data_file)["DATABASE"]
print(database["user"])


try:  # database config
    connect_str = f"dbname='{database['db_name']}' user='{database['user']}' host='{database['host']}' password='{database['password']}'"
    conn = psycopg2.connect(connect_str)
    cursor = conn.cursor()
except Exception as e:
    print(e)


cursor.execute(
    """SELECT id, sp_id, name, street, city, zip FROM restaurants_sp WHERE name NOT LIKE '%Dostava%' AND name NOT LIKE '%dostava%' """)

counter = 0
for restaurant_sp in cursor.fetchall():
    
    ime_restavracije = restaurant_sp[2].replace("'", "").replace("restavracija ", "").replace(
        "pizzerija", "").replace("Restavracija ", "").replace("Pizzerija", "").replace("in ", "").split()

    street_array = restaurant_sp[3].replace("cesta", "").replace("Cesta", "").replace("ulica", "").replace("Ulica", "").split()
    street = restaurant_sp[3]

    query2 = f"""
        SELECT id, name, street FROM restaurants WHERE 
        zip = '{restaurant_sp[5]}'
        AND LOWER(street) = LOWER('{street}')
        AND LOWER(name) SIMILAR TO LOWER(\'%({(' | ').join(ime_restavracije)})%\')
        """
    cursor.execute(query2)

    if (len(cursor.fetchall()) != 0):
        # counter += 1
        # print(counter)
        cursor.execute(query2)
        for match in cursor.fetchall():
            print("\n")
            print("resaurant: ", match)
            print("studentska: ", restaurant_sp)
            is_equal = input("Combine? ")

            if (is_equal != "n"):
                print("okidoki")
                update_quety =  f""" UPDATE restaurants SET restaurant_sp_id = {restaurant_sp[1]} WHERE id = {match[0]}"""
                cursor.execute(update_quety)
                update_quety_2 =  f""" UPDATE restaurants_sp SET connected = TRUE WHERE sp_id = {restaurant_sp[1]}"""
                cursor.execute(update_quety_2)
                conn.commit()
            