from flask import Flask, jsonify
from flask_cors import CORS
from db import fetch_airports

app = Flask(__name__)
CORS(app)

# Пример данных маркеров
markers_data = {
    "data": [
        {"ICAO": "1", "position": [51.505, -0.09], "name": "London", "type": "red"},
        {"ICAO": "2", "position": [48.8566, 2.3522], "name": "Paris", "type": "diamond"},
        {"ICAO": "3", "position": [40.7128, -74.0060], "name": "New York", "type": "topaz"},
    ]
}
0
@app.route('/get_markers', methods=['GET'])
def get_markers():
    airports = fetch_airports()
    print(len(airports))
    print((airports))
    return jsonify(airports)
    # return jsonify(markers_data)

if __name__ == '__main__':
    app.run(host='localhost', port=4000, debug=True)