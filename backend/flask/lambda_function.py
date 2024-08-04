import awsgi
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import json
import mysql.connector


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/', methods=['GET'])
@cross_origin()
def main():
    # Connect to DB
    cnx = mysql.connector.connect(**credentials())
    cursor = cnx.cursor()

    sql = f"""
        SELECT NAME, HIST_AVG, FORECAST, DISCREPANCY FROM FORECASTS F
        INNER JOIN CITIES C ON F.CITY_ID = C.ID
    """

    cursor.execute(sql)
    result = cursor.fetchall()

    cursor.close()
    cnx.close()

    data = {}

    for row in result:
        data[row[0]] = [row[1], row[2], row[3]]

    return jsonify({
        'statusCode': 200,
        'body': data
    })


def credentials():
    with open('dbcreds.json') as file:
        return json.load(file)


def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})