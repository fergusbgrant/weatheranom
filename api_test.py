import requests


def main():
    city = 'Dublin'
    url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=en&format=json'
    results = requests.get(url).json()

    for result in results['results']:
        if result['country_code'] == 'IE':
            lat, lon = result['latitude'], result['longitude']
            break

    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&forecast_days=16'
    results = requests.get(url).json()

    print(results)
    

if __name__ == '__main__':
    main()