import json
import mysql
import requests

import mysql.connector


def lambda_handler(event, context):
    city = 'Dublin'
    url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=en&format=json'
    results = requests.get(url).json()

    for result in results['results']:
        if result['country_code'] == 'IE':
            lat, lon = result['latitude'], result['longitude']
            break

    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&forecast_days=16'
    results = requests.get(url).json()

    cnx = mysql.connector.connect(**credentials())
    cursor = cnx.cursor()
    sql = 'SELECT * FROM TEST'
    cursor.execute(sql)
    result = cursor.fetchall()
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }


def credentials():
    with open('dbcreds.json') as file:
        return json.load(file)


if __name__ == '__main__':
    lambda_handler()