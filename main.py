from flask import Flask, request, jsonify
from flask_cors import CORS
from db import fetch_airports, update_game_manager_in_db, update_game_markers_in_db

app = Flask(__name__)
CORS(app)


# Endpoint for the primary generation of airports
@app.route('/get_markers', methods=['GET'])
def get_markers():
    airports = fetch_airports()
    print(airports)
    return jsonify(airports)



# Endpoint for updating the at_game_manager table
@app.route('/update_game_manager', methods=['POST'])
def update_game_manager_endpoint():
    data = request.json
    result = update_game_manager_in_db(data)
    return jsonify(result)


# Endpoint for updating the at_game_markers table
@app.route('/update_game_markers', methods=['POST'])
def update_game_markers():
    data = request.json
    result = update_game_markers_in_db(data['markers'])
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='localhost', port=4000, debug=True)