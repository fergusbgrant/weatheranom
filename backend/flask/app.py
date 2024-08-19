import awsgi
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import json
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/', methods=['GET'])
@cross_origin()
def index():
    # Connect to DB
    cnx = mysql.connector.connect(**credentials())
    cursor = cnx.cursor()

    sql = f"""
        SELECT NAME, ISO, HIST_AVG, FORECAST, DISCREPANCY FROM FORECASTS F
        INNER JOIN CITIES C ON F.CITY_ID = C.ID
        ORDER BY ABS(DISCREPANCY) DESC
    """

    cursor.execute(sql)
    result = cursor.fetchall()

    cursor.close()
    cnx.close()

    data = []

    for row in result:
        data.append({
            'city': row[0],
            'country': row[1],
            'historical': row[2],
            'forecast': row[3],
            'discrepancy': row[4]
        })
                        
    return jsonify({
        'responseCode': 200,
        'body': data
    })


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.json['username']
        password = generate_password_hash(request.json['password'])

        cnx = mysql.connector.connect(**credentials())
        cursor = cnx.cursor()

        sql = f"""
            INSERT INTO USERS (USERNAME, PASSHASH) VALUES ('{username}','{password}')
        """

        cursor.execute(sql)
        cnx.commit()

        cursor.close()
        cnx.close()

        return jsonify({
            "responseCode": 200,
            "body": {
                "username": username,
                "hash": password
            }
        })
    
    elif request.method == 'GET':
        return jsonify({
            'responseCode': 200,
            'body': 'poo'
        })


def credentials():
    with open('dbcreds.json') as file:
        return json.load(file)


def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})