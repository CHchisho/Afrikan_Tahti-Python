import json
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



def fetch_airports(limit=20, max_connections=3):
    """Возвращает данные всех аэропортов, исключая heliport и closed."""
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            # SQL-запрос для получения необходимых данных
            query = """
            SELECT 
                a.id, 
                a.ident AS ICAO, 
                a.type, 
                a.name, 
                a.latitude_deg, 
                a.longitude_deg, 
                a.iso_country,
                c.wikipedia_link
            FROM 
                airport a
            JOIN 
                country c
            ON 
                a.iso_country = c.iso_country
            WHERE 
                a.type NOT IN ('heliport', 'closed', 'seaplane_base', 'balloonport')
                AND a.iso_country IN (
                    'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 
                    'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'KZ', 
                    'XK', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL', 'MK', 'NO', 
                    'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR', 
                    'UA', 'GB', 'VA'
                )
            GROUP BY 
                a.iso_country
            LIMIT %s;
            """
#             query = """
# SELECT
#     id,
#     ident AS ICAO,
#     type,
#     name,
#     latitude_deg,
#     longitude_deg,
#     iso_country
# FROM
#     airport
# WHERE
#     type NOT IN ('heliport', 'closed', 'seaplane_base', 'balloonport')
#     AND iso_country IN (
#         'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ',
#         'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'KZ',
#         'XK', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL', 'MK', 'NO',
#         'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR',
#         'UA', 'GB', 'VA'
#     )
# GROUP BY
#     iso_country
# LIMIT %s;
#             """
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
                    "iso_country": airport["iso_country"],
                    "wikipedia_link": airport["wikipedia_link"],
                }
                for airport in airports
            ]


            # icao_list = [airport["ICAO"] for airport in formatted_airports]
            # # icao_connections = []
            # icao_connections = set()
            # for icao in icao_list:
            #     num_connections = random.randint(2, max_connections)
            #     possible_connections = [other_icao for other_icao in icao_list if other_icao != icao]
            #     random_connections = random.sample(possible_connections,
            #                                        min(num_connections, len(possible_connections)))
            #
            #     # Получение текущего аэропорта
            #     current_airport = next(airport for airport in formatted_airports if airport["ICAO"] == icao)
            #     current_position = current_airport["position"]
            #
            #     for conn in random_connections:
            #         connected_airport = next(airport for airport in formatted_airports if airport["ICAO"] == conn)
            #         connected_position = connected_airport["position"]
            #
            #         # Вычисление расстояния между аэропортами
            #         distance = geodesic(current_position, connected_position).kilometers
            #
            #         # Добавление соединения с расстоянием
            #         icao_connections.add((icao, conn, int(distance)))
            #         # icao_connections.add((conn, icao, int(distance)))
            # print("connections:",len(icao_connections), icao_connections)
            # icao_connections = list(icao_connections)


            icao_list = [airport["ICAO"] for airport in formatted_airports]
            unique_connections_set = set()
            unique_connections = []

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

                    # Расстояния между аэропортами
                    distance = geodesic(current_position, connected_position).kilometers
                    # Создание кортежа соединения с расстоянием
                    icao_connection = (icao, conn, int(distance))
                    # Сортируем первые два элемента и создаем кортеж
                    ordered_connection = tuple(sorted(icao_connection[:2])) + (icao_connection[2],)

                    # Если комбинации еще нет в множестве
                    if ordered_connection not in unique_connections_set:
                        unique_connections_set.add(ordered_connection)
                        unique_connections.append(icao_connection)

            print("connections:", len(unique_connections), unique_connections)


            return {"data":formatted_airports,"icao_connections":unique_connections}
        except Error as e:
            print(f"Error fetching airports: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return []



# Функция для добавления данных в таблицу at_game_manager
def update_game_manager_in_db(data):
    connection = get_connection()
    if connection is None:
        return {"error": "Failed to connect to database"}

    try:
        cursor = connection.cursor()
        # Удаление всех данных из таблицы
        cursor.execute("TRUNCATE TABLE at_game_manager")

        query = """
        INSERT INTO at_game_manager (game_status, current_money, current_fuel, currentAirport, visitedAirports, visitedPaths, discoveredPaths, suggestedPaths, diamondFound, game_user_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['game_status'],
            data['current_money'],
            data['current_fuel'],
            json.dumps(data['currentAirport']),
            json.dumps(data['visitedAirports']),
            json.dumps(data['visitedPaths']),
            json.dumps(data['discoveredPaths']),
            json.dumps(data['suggestedPaths']),
            data['diamondFound'],
            data['game_user_name'],
        ))
        connection.commit()
        print("update_game_manager")
        return {"success": "Data inserted successfully"}
    except Error as e:
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Функция для добавления данных в таблицу at_game_markers
def update_game_markers_in_db(markers):
    connection = get_connection()
    if not connection:
        return {'status': 'fail', 'message': 'Database connection failed'}

    try:
        cursor = connection.cursor()

        # Удаление всех данных из таблицы
        cursor.execute("TRUNCATE TABLE at_game_markers")

        # Вставка новых данных
        for marker in markers:
            icao = marker.get('ICAO')
            position = marker.get('position')
            name = marker.get('name')
            type_ = marker.get('type')
            discovered = marker.get('discovered', False)

            if icao and position and name and type_:
                lat_pos, lon_pos = position
                query = """
                INSERT INTO at_game_markers (ICAO, lat_pos, lon_pos, name, type, discovered)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    lat_pos = VALUES(lat_pos),
                    lon_pos = VALUES(lon_pos),
                    name = VALUES(name),
                    type = VALUES(type),
                    discovered = VALUES(discovered)
                """
                cursor.execute(query, (icao, lat_pos, lon_pos, name, type_, discovered))

        connection.commit()
        print("update_game_markers")
        return {"success": "Data inserted successfully"}
    except Error as e:
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
# def update_game_markers_in_db(markers):
#     connection = get_connection()
#     if not connection:
#         return {'status': 'fail', 'message': 'Database connection failed'}
#
#     try:
#         cursor = connection.cursor()
#         # Удаление всех данных из таблицы
#         cursor.execute("TRUNCATE TABLE at_game_markers")
#
#         for marker in markers:
#             # Извлекаем значения с помощью .get(), чтобы избежать KeyError
#             icao = marker.get('ICAO')
#             position = marker.get('position')
#             name = marker.get('name')
#             type_ = marker.get('type')
#             discovered = marker.get('discovered', False)  # Значение по умолчанию
#
#             if icao and position and name and type_:
#                 position_wkt = f"POINT({position[1]} {position[0]})"
#                 query = """
#                 INSERT INTO at_game_markers (ICAO, position, name, type, discovered)
#                 VALUES (%s, ST_GeomFromText(%s), %s, %s, %s)
#                 ON DUPLICATE KEY UPDATE
#                     position = VALUES(position),
#                     name = VALUES(name),
#                     type = VALUES(type),
#                     discovered = VALUES(discovered)
#                 """
#                 cursor.execute(query, (icao, position_wkt, name, type_, discovered))
#             else:
#                 # Можно добавить логирование или обработку отсутствующих данных
#                 print(f"Skipping invalid marker: {marker}")
#
#         connection.commit()
#         print("update_game_markers")
#         return {'status': 'success', 'message': 'Markers updated'}
#     except Error as e:
#         return {'status': 'fail', 'message': str(e)}
#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()





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


# Создание кастомных таблиц
# def create_tables():
#     connection = None
#     try:
#         connection = mysql.connector.connect(**config)
#         if connection.is_connected():
#             cursor = connection.cursor()
#
#             # SQL запросы для создания таблиц
#             create_at_game_manager = """
#             CREATE TABLE IF NOT EXISTS at_game_manager (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 game_status VARCHAR(255),
#                 current_money VARCHAR(255),
#                 current_fuel VARCHAR(255),
#                 currentAirport JSON,
#                 visitedAirports JSON,
#                 visitedPaths JSON,
#                 discoveredPaths JSON,
#                 suggestedPaths JSON,
#                 diamondFound BOOLEAN
#             );
#             """
#
#             create_at_game_markers = """
#             CREATE TABLE IF NOT EXISTS at_game_markers (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 ICAO VARCHAR(10),
#                 position JSON,
#                 name VARCHAR(255),
#                 type VARCHAR(50),
#                 discovered BOOLEAN
#             );
#             """
#
#             # Выполнение запросов
#             cursor.execute(create_at_game_manager)
#             cursor.execute(create_at_game_markers)
#
#             connection.commit()
#             print("Tables created successfully")
#
#     except Error as e:
#         print(f"Error while connecting to MySQL: {e}")
#     finally:
#         if connection and connection.is_connected():
#             cursor.close()
#             connection.close()

# create_tables()


# Обновление кастомных таблиц
# def create_tables():
#     connection = None
#     try:
#         connection = mysql.connector.connect(**config)
#         if connection.is_connected():
#             cursor = connection.cursor()
#
#             # SQL запросы для создания таблиц
#             create_at_game_manager = """
# ALTER TABLE at_game_markers
# DROP COLUMN position,
# ADD COLUMN lat_pos DOUBLE NOT NULL,
# ADD COLUMN lon_pos DOUBLE NOT NULL;
#             """
#
#             # Выполнение запросов
#             cursor.execute(create_at_game_manager)
#
#             connection.commit()
#             print("Tables created successfully")
#
#     except Error as e:
#         print(f"Error while connecting to MySQL: {e}")
#     finally:
#         if connection and connection.is_connected():
#             cursor.close()
#             connection.close()
#
# create_tables()

# Обновление кастомных таблиц
# def create_tables():
#     connection = None
#     try:
#         connection = mysql.connector.connect(**config)
#         if connection.is_connected():
#             cursor = connection.cursor()
#
#             # SQL запрос для добавления нового столбца
#             create_at_game_manager = """
#             ALTER TABLE at_game_manager
#             ADD COLUMN game_user_name VARCHAR(255) NOT NULL
#             """
#
#             # Выполнение запроса
#             cursor.execute(create_at_game_manager)
#
#             connection.commit()
#             print("Column added successfully")
#
#     except Error as e:
#         print(f"Error while connecting to MySQL: {e}")
#     finally:
#         if connection and connection.is_connected():
#             cursor.close()
#             connection.close()
#
# create_tables()
