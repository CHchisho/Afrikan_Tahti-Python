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
    """Returns a connection to the database."""
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


# Generates airports and connections
def fetch_airports(limit=20, max_connections=3):
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            # SQL query to get the required data
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
                    'DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CG', 'CD', 
                    'DJ', 'EG', 'GQ', 'ER', 'SZ', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'CI', 'KE', 
                    'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MU', 'MA', 'MZ', 'NA', 'NE', 'NG', 
                    'RW', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'TZ', 'TG', 'TN', 'UG', 
                    'EH', 'ZM', 'ZW'
                )
            GROUP BY 
                a.iso_country
            LIMIT %s;
            """
            cursor.execute(query, (limit,))
            airports = cursor.fetchall()

            # 'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ',
            # 'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'KZ',
            # 'XK', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL', 'MK', 'NO',
            # 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR',
            # 'UA', 'GB', 'VA'

            # Definition of types and quantity of each type
            types = {
                "topaz": 4, # 300
                "emerald": 3, # 600
                "ruby": 2, # 1000
                "bandit": 3,
                "diamond": 1,
                "home": 1
            }
            # Select random airports for each type
            chosen_airports = random.sample(airports, sum(types.values()))
            # Assign types to selected airports
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
            # The remaining airports remain with the "empty" type
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


            icao_list = [airport["ICAO"] for airport in formatted_airports]
            unique_connections_set = set()
            unique_connections = []

            for icao in icao_list:
                # num_connections = random.randint(3, max_connections)
                num_connections = 3
                possible_connections = [other_icao for other_icao in icao_list if other_icao != icao]
                random_connections = random.sample(possible_connections,
                                                   min(num_connections, len(possible_connections)))

                # Get the current airport
                current_airport = next(airport for airport in formatted_airports if airport["ICAO"] == icao)
                current_position = current_airport["position"]

                for conn in random_connections:
                    connected_airport = next(airport for airport in formatted_airports if airport["ICAO"] == conn)
                    connected_position = connected_airport["position"]

                    # Distances between airports
                    distance = geodesic(current_position, connected_position).kilometers
                    # Create a join tuple with distance
                    icao_connection = (icao, conn, int(distance))
                    # Sort the first two elements and create a tuple
                    ordered_connection = tuple(sorted(icao_connection[:2])) + (icao_connection[2],)

                    # If the combination is not yet in the set
                    # if ordered_connection not in unique_connections_set:
                    if ordered_connection not in unique_connections_set:
                        unique_connections_set.add(ordered_connection)
                        unique_connections.append(icao_connection)


            return {"data":formatted_airports,"icao_connections":unique_connections}
        except Error as e:
            print(f"Error fetching airports: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return []


# Function to add data to the at_game_manager table
def update_game_manager_in_db(data):
    connection = get_connection()
    if connection is None:
        return {"error": "Failed to connect to database"}

    try:
        cursor = connection.cursor()
        # Remove all data from a table
        cursor.execute("TRUNCATE TABLE at_game_manager")

        query = """
        INSERT INTO at_game_manager (game_status, current_money, current_fuel, currentAirport, visitedAirports, visitedPaths, discoveredPaths, suggestedPaths, diamondFound, game_user_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['game_status'],
            data['current_money'],
            data['current_fuel'],
            data['currentAirport']["ICAO"],
            json.dumps(data['visitedAirports']),
            json.dumps(data['visitedPaths']),
            json.dumps(data['discoveredPaths']),
            json.dumps(data['suggestedPaths']),
            data['diamondFound'],
            data['game_user_name'],
        ))
        connection.commit()
        # print("update_game_manager")
        return {"success": "Data inserted successfully"}
    except Error as e:
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Function to add data to the at_game_markers table
def update_game_markers_in_db(markers):
    connection = get_connection()
    if not connection:
        return {'status': 'fail', 'message': 'Database connection failed'}

    try:
        cursor = connection.cursor()

        # Remove all data from a table
        cursor.execute("TRUNCATE TABLE at_game_markers")

        # Inserting new data
        for marker in markers:
            icao = marker.get('ICAO')
            type_ = marker.get('type')
            discovered = marker.get('discovered', False)

            if icao and type_:
                query = """
                INSERT INTO at_game_markers (ICAO, type, discovered)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    ICAO = VALUES(ICAO),
                    type = VALUES(type),
                    discovered = VALUES(discovered)
                """
                cursor.execute(query, (icao, type_, discovered))

        connection.commit()
        # print("update_game_markers")
        return {"success": "Data inserted successfully"}
    except Error as e:
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



# Creating custom tables
def create_tables():
    connection = None
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor()

            # SQL query to create the at_game_manager table
            create_at_game_manager = """
            CREATE TABLE IF NOT EXISTS at_game_manager (
                id INT AUTO_INCREMENT PRIMARY KEY,
                game_status VARCHAR(40),
                current_money VARCHAR(40),
                current_fuel VARCHAR(40),
                currentAirport VARCHAR(10),
                visitedAirports JSON,
                visitedPaths JSON,
                discoveredPaths JSON,
                suggestedPaths JSON,
                diamondFound BOOLEAN,
                game_user_name VARCHAR(40) NOT NULL
            );
            """

            create_at_game_markers = """
            CREATE TABLE IF NOT EXISTS at_game_markers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ICAO VARCHAR(10),
                type VARCHAR(40),
                discovered BOOLEAN
                # INDEX (ICAO),
                # FOREIGN KEY (ICAO) REFERENCES airport(ident)
            );
            """

            cursor.execute(create_at_game_manager)
            cursor.execute(create_at_game_markers)

            connection.commit()
            print("Tables created successfully, if they did not already exist.")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

create_tables()