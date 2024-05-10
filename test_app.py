from flask import Flask, render_template, request, jsonify
import requests
import os
import psycopg2
from datetime import datetime
import sys
import json


API_KEY = '2011c5e9bd90ba0922ab2b165dc0d27b'
WEATHER_URL = 'http://api.openweathermap.org/data/3.0/onecall'
GEO_URL = 'http://api.openweathermap.org/geo/1.0/direct'

def get_geo(city):
    params = {'q': city, 'limit': '1', 'appid': API_KEY, }
    try:
        response = requests.get(GEO_URL, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        print(data)
        for val in data:
            lat_long = {'latitude': val['lat'], 'longitude': val['lon']}
        print(lat_long)
        return lat_long
    except requests.exceptions.RequestException as e:
        return {'error': f"Failed to fetch weather data: {e}"}

def get_weather(lat_lon):
    params = {'lat': lat_lon['latitude'], 'lon': lat_lon['longitude'], 'appid': API_KEY, 'units': 'standard'}
    try:
        response = requests.get(WEATHER_URL, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return {'error': f"Failed to fetch weather data: {e}"}

def main():
    city = input("Enter city name: ")
    city_lat_lon = get_geo(city)
    weather_data = get_weather(city_lat_lon)
    try:
        weather = {
            'city': city,
            'temperature': weather_data['current']['temp'],
            'description': weather_data['current']['weather'][0]['description']
        }
        print(json.dumps(weather, indent=4))
    except:
        error_message = weather_data['message']
        print(f"Error: {error_message}")

if __name__ == "__main__":
    main()
