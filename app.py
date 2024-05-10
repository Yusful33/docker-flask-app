from flask import Flask, render_template, request, jsonify
import requests
import os
import psycopg2
from datetime import datetime
import sys
import os


WEATHER_URL = 'http://api.openweathermap.org/data/3.0/onecall'
GEO_URL = 'http://api.openweathermap.org/geo/1.0/direct'

app = Flask(__name__)
app.config['DEBUG'] = True

def get_secret(secret_name):
    try:
        with open(f'/run/secrets/{secret_name}') as secret_file:
            return secret_file.read().strip()
    except IOError:
        return None

def get_geo(city):
    params = {'q': city, 'limit': '1', 'appid': get_secret('api-key')}
    try:
        response = requests.get(GEO_URL, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        for val in data:
            lat_long = {'latitude': val['lat'], 'longitude': val['lon']}
        print(lat_long)
        return lat_long
    
    except requests.exceptions.RequestException as e:
        return {'error': f"Failed to fetch weather data: {e}"}



def get_weather(lat_lon):
     # Check if the required keys are present
    required_keys = ['latitude', 'longitude']
    for key in required_keys:
        if key not in lat_lon:
            raise KeyError(f"Missing key: {key}")
    latitude = lat_lon['latitude']
    longitude = lat_lon['longitude']
    input_vars = {'lat': latitude, 'lon': longitude, 'appid': get_secret('api-key'), 'units': 'standard'}
    try:
        response = requests.get(WEATHER_URL, params=input_vars)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return {'error': f"Failed to fetch weather data: {e}"}


# Connect to PostgreSQL database
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname='weather_info',
            user='weather_user',
            password=os.getenv('POSTGRES_PASSWORD'),
            host='db', 
            port='5432'
        )
        return conn
    except psycopg2.Error as e:
        print("Unable to connect to the database:", e)
        sys.exit(1)

# Function to create table
def create_table():
    conn = connect_to_db()
    with conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS weather_data (
                      id SERIAL PRIMARY KEY,
                      date DATE,
                      time TIME,
                      city VARCHAR(255),
                      temperature FLOAT,
                      description TEXT
                      )''')
    conn.close()

# Insert data into the database
def insert_data(city, temperature, description):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO weather_data (id, date, time, city, temperature, description)
                      VALUES (DEFAULT, CURRENT_DATE, CURRENT_TIME, %s, %s, %s)''', (city, temperature, description))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        city = request.form.get('city')
        city_lat_lon = get_geo(city)
        print(city_lat_lon)
        weather_data = get_weather(city_lat_lon)
        try:
            weather = {
                'city': city,
                'temperature': weather_data['current']['temp'],
                'description': weather_data['current']['weather'][0]['description']
            }
             # Insert data into database
            insert_data(weather['city'], weather['temperature'], weather['description'])
            return render_template('weather.html', weather=weather)
        except:
            error_message = weather_data['message']
            return render_template('weather.html', error=error_message)
    return render_template('weather.html')

if __name__ == "__main__":
    create_table()
    print(get_secret('api-key'))
    app.run(host="0.0.0.0", debug=True, port="8000")