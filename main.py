from flask import Flask, request, jsonify
from flask_cors import CORS
from db import fetch_airports, update_game_manager_in_db, update_game_markers_in_db

app = Flask(__name__)
CORS(app)

# Пример данных маркеров
# markers_data = {
#     "data": [
#         {"ICAO": "1", "position": [51.505, -0.09], "name": "London", "type": "red"},
#         {"ICAO": "2", "position": [48.8566, 2.3522], "name": "Paris", "type": "diamond"},
#         {"ICAO": "3", "position": [40.7128, -74.0060], "name": "New York", "type": "topaz"},
#     ]
# }

@app.route('/get_markers', methods=['GET'])
def get_markers():
    airports = fetch_airports()
    print(len(airports))
    print((airports))
    return jsonify(airports)
    # return jsonify(markers_data)



# Эндпоинт для обновления таблицы at_game_manager
@app.route('/update_game_manager', methods=['POST'])
def update_game_manager_endpoint():
    data = request.json
    result = update_game_manager_in_db(data)
    return jsonify(result)


@app.route('/update_game_markers', methods=['POST'])
def update_game_markers():
    data = request.json
    result = update_game_markers_in_db(data['markers'])
    return jsonify(result)
    # if 'markers' in data:
    #     result = update_game_markers_in_db(data['markers'])
    #     return jsonify(result)
    # return jsonify({'status': 'fail', 'message': 'Invalid data'}), 400


if __name__ == '__main__':
    app.run(host='localhost', port=4000, debug=True)