from flask import Flask, request, jsonify
import pypyodbc
import json
from urllib.parse import urlparse

app = Flask(__name__)

# Установка соединения с базой данных

DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'WIN-50VPF1OFR1I\\SQLEXPRESS'
DATABASE_NAME = 'dev-db'

connectionString = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={{{SERVER_NAME}}};
    DATABASE={{{DATABASE_NAME}}};
    Trust_Connection=yes;
"""

connection = pypyodbc.connect(connectionString)

# Создание курсор
cursor = connection.cursor()


@app.route('/api/data', methods=['GET'])
def get_data():
    try:

        parsedQuery = urlparse(request.url)

        parameters = {}
        _parameters = parsedQuery.query.split('&')

        for _p in _parameters:
            _tokens = _p.split('=')
            _key = _tokens[0]
            _value = _tokens[1]
            parameters[_key] = _value

        room = parameters["room"]
        date = parameters["date"]

        sql = "SELECT StartTime, EndTime, GroupTitle, Description, Id FROM event  " \
              "WHERE roomid = (SELECT id FROM Room WHERE title = ?) AND date = ?"

        params = (room, date)

        cursor.execute(sql, params)

        rows = cursor.fetchall()

        results = []
        for row in rows:
            result = {
                'StartTime': row[0],
                'EndTime': row[1],
                'GroupTitle': row[2],
                'Description': row[3],
                'Id': row[4]
            }
            results.append(result)

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/data', methods=['POST'])
def add_data():
    try:
        data = json.loads(request.data)
        room = data['room']
        group = data['group']
        date = data['date']
        startTime = data['startTime']
        endTime = data['endTime']
        description = data['description']

        sql = "INSERT INTO Event (RoomTitle, GroupTitle, Date, StartTime, EndTime, Description, RoomId, GroupId ) " \
              "VALUES (?, ?, ?, ?, ?, ?, (SELECT id FROM Room WHERE title = ?), " \
              "(SELECT id FROM Groups WHERE title = ?))"

        params = (room, group, date, startTime, endTime, description, room, group)

        cursor.execute(sql, params)

        connection.commit()

        return jsonify({'message': 'Data added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/data', methods=['DELETE'])
def delete_data():
    try:
        parsedQuery = urlparse(request.url)

        parameters = {}
        _parameters = parsedQuery.query.split('&')

        for _p in _parameters:
            _tokens = _p.split('=')
            _key = _tokens[0]
            _value = _tokens[1]
            parameters[_key] = _value

        trainId = parameters["id"]

        sql = "DELETE FROM Event WHERE ID = ?"

        cursor.execute(sql, (trainId,))

        connection.commit()

        return jsonify({'message': 'Data deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
