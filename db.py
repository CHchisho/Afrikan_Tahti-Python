import random
import mysql.connector
from mysql.connector import Error
from geopy.distance import geodesic

config = {
    'user': 'ilia',
    'password': 'password',
    'host': 'localhost',
    'database': 'flight_game',
    'port': 3306
}

def get_connection():
    """Возвращает подключение к базе данных."""
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None



def fetch_airports(limit=30, max_connections=3):
    """Возвращает данные всех аэропортов, исключая heliport и closed."""
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            # SQL-запрос для получения необходимых данных
            # query = """
            # SELECT id, ident AS ICAO, type, name, latitude_deg, longitude_deg
            # FROM airport
            # WHERE type NOT IN ('heliport', 'closed')
            # AND iso_country IN (
            #     'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ',
            #     'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'KZ',
            #     'XK', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL', 'MK', 'NO',
            #     'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR',
            #     'UA', 'GB', 'VA'
            # )
            # LIMIT %s
            # """
            query = """
SELECT 
    id, 
    ident AS ICAO, 
    type, 
    name, 
    latitude_deg, 
    longitude_deg, 
    iso_country
FROM 
    airport
WHERE 
    type NOT IN ('heliport', 'closed', 'seaplane_base', 'balloonport')
    AND iso_country IN (
        'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 
        'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'KZ', 
        'XK', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL', 'MK', 'NO', 
        'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR', 
        'UA', 'GB', 'VA'
    )
GROUP BY 
    iso_country
LIMIT %s;
            """
            cursor.execute(query, (limit,))
            airports = cursor.fetchall()


            # Определение типов и количества каждого типа
            types = {
                "topaz": 4, # 300
                "emerald": 3, # 600
                "ruby": 2, # 1000
                "bandit": 3,
                "diamond": 1,
                "home": 1
            }
            # Выбираем случайные аэропорты для каждого типа
            chosen_airports = random.sample(airports, sum(types.values()))
            # Назначаем выбранным аэропортам типы
            for i, airport in enumerate(chosen_airports):
                if i < types["topaz"]:
                    airport["type"] = "topaz"
                elif i < types["topaz"] + types["emerald"]:
                    airport["type"] = "emerald"
                elif i < types["topaz"] + types["emerald"] + types["ruby"]:
                    airport["type"] = "ruby"
                elif i < types["topaz"] + types["emerald"] + types["ruby"] + types["bandit"]:
                    airport["type"] = "bandit"
                elif i < types["topaz"] + types["emerald"] + types["ruby"] + types["bandit"] + types["diamond"]:
                    airport["type"] = "diamond"
                else:
                    airport["type"] = "home"
            # Остальные аэропорты остаются с типом "empty"
            for airport in airports:
                if airport["type"] not in types.keys():
                    airport["type"] = "empty"



            formatted_airports = [
                {
                    "ICAO": airport["ICAO"],
                    "position": [airport["latitude_deg"], airport["longitude_deg"]],
                    "name": airport["name"],
                    "type": airport["type"],
                    "discovered": False,
                }
                for airport in airports
            ]


            icao_list = [airport["ICAO"] for airport in formatted_airports]
            # icao_connections = []
            icao_connections = set()
            for icao in icao_list:
                num_connections = random.randint(2, max_connections)
                possible_connections = [other_icao for other_icao in icao_list if other_icao != icao]
                random_connections = random.sample(possible_connections,
                                                   min(num_connections, len(possible_connections)))

                # Получение текущего аэропорта
                current_airport = next(airport for airport in formatted_airports if airport["ICAO"] == icao)
                current_position = current_airport["position"]

                for conn in random_connections:
                    connected_airport = next(airport for airport in formatted_airports if airport["ICAO"] == conn)
                    connected_position = connected_airport["position"]

                    # Вычисление расстояния между аэропортами
                    distance = geodesic(current_position, connected_position).kilometers

                    # Добавление соединения с расстоянием
                    icao_connections.add((icao, conn, int(distance)))
                    # icao_connections.add((conn, icao, int(distance)))
            print("connections:",len(icao_connections), icao_connections)
            icao_connections = list(icao_connections)

            return {"data":formatted_airports,"icao_connections":icao_connections}
        except Error as e:
            print(f"Error fetching airports: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []




# def test(limit=30, max_connections=3):
#     """Возвращает данные всех аэропортов, исключая heliport и closed."""
#     connection = get_connection()
#     if connection:
#         try:
#             cursor = connection.cursor(dictionary=True)
#             query = """
# SELECT type, COUNT(*) as count
# FROM airport
# GROUP BY type
# ORDER BY count DESC;
#
#             """
#             cursor.execute(query)
#             airports = cursor.fetchall()
#             print(airports)
#
#
#         except Error as e:
#             print(f"Error fetching airports: {e}")
#             return []
#         finally:
#             cursor.close()
#             connection.close()
#     return []
# test()