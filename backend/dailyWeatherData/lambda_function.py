import datetime
import json
import requests
import mysql.connector


def lambda_handler(event, context):
    # Connect to DB
    cnx = mysql.connector.connect(**credentials())
    cursor = cnx.cursor()
    
    # Call functions to get average temps for next 16 days,
    # and the historical averages for the same 16-day period
    forecast = get_forecast(cursor)
    hist_avgs = get_historical_avgs(cursor)

    # Add historical averages and discrepancy figures to forecast dicts
    for city in hist_avgs:
        forecast[city[0]].append(city[1])
        forecast[city[0]].append(round(abs(forecast[city[0]][0] - city[1]), 2))

    # Remove yesterday's prediction from DB
    sql = """
        TRUNCATE TABLE FORECASTS
    """
    cursor.execute(sql)

    # Create string of values for DB table insert
    forecast_str = ''
    first = True
    for city in forecast:
        if first == True:
            forecast_str += f"({city},{forecast[city][1]},{forecast[city][0]},{forecast[city][2]})"
            first = False
        else:
            forecast_str += f",({city},{forecast[city][1]},{forecast[city][0]},{forecast[city][2]})"

    # Write forecasts to the DB
    sql = f"""
        INSERT INTO FORECASTS (CITY_ID, HIST_AVG, FORECAST, DISCREPANCY) VALUES {forecast_str}
    """
    cursor.execute(sql)
    cnx.commit()

    # Close connection to DB
    cursor.close()
    cnx.close()
        

def credentials():
    with open('dbcreds.json') as file:
        return json.load(file)
    

def get_forecast(cursor):
    # Get city lats and lons for forecast API call
    sql = """
        SELECT ID, LAT, LON FROM CITIES
    """
    cursor.execute(sql)
    cities = cursor.fetchall()

    # Get forecast for each city and make entry in forecast dict
    forecast = {}
    for city in cities:
        url = f'https://api.open-meteo.com/v1/forecast?latitude={city[1]}&longitude={city[2]}&daily=temperature_2m_max,temperature_2m_min&forecast_days=16'
        response = requests.get(url).json()
        avg = round((sum(response['daily']['temperature_2m_max']) + sum(response['daily']['temperature_2m_min'])) / 32, 2)
        forecast[city[0]] = [avg]

    return forecast


def get_historical_avgs(cursor):
    # Get current date to query the relevant historical 16-day periods
    now = datetime.datetime.now()
    sql = f"""
    WITH RECURSIVE TEMP_IDS AS (
        SELECT ID, 0 AS N FROM HISTORICAL_TEMPS
        WHERE (
            DAY = {now.strftime(r'%d')}
            AND MONTH = {now.strftime(r'%m')}
        )
        UNION ALL
        SELECT ID + 1, N + 1 FROM TEMP_IDS
        WHERE N < 15
    )
    SELECT CITY_ID, ROUND(AVG(AVG_TEMPERATURE), 2) FROM TEMP_IDS TI
    INNER JOIN HISTORICAL_TEMPS HT ON TI.ID = HT.ID
    GROUP BY CITY_ID
    """
    cursor.execute(sql)
    return cursor.fetchall()
    

if __name__ == '__main__':
    lambda_handler()