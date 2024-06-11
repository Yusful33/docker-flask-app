from flask import Flask, render_template, request, jsonify
import requests
import os
import psycopg2
from datetime import datetime
import sys
import os
import logging
from flask_cors import CORS
from decimal import Decimal



WEATHER_URL = 'http://api.openweathermap.org/data/3.0/onecall'
GEO_URL = 'http://api.openweathermap.org/geo/1.0/direct'

app = Flask(__name__)
CORS(app)
app.config['DEBUG'] = True
app.logger.setLevel(logging.INFO)


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
def connect_to_db(db_name, db_user):
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=os.getenv('POSTGRES_PASSWORD'),
            host='db', 
            port='5432'
        )
        return conn
    except psycopg2.Error as e:
        print("Unable to connect to the database:", e)
        sys.exit(1)

# Insert data into the database
def insert_weather_data(city, temperature, description):
    conn = connect_to_db('weather_info', 'weather_user')
    cursor = conn.cursor()
    cursor.execute('''select * from information_schema.tables''')
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
            app.logger.info(f'Current role being leveraged {weather}')
             # Insert data into database
            insert_weather_data(weather['city'], weather['temperature'], weather['description'])
            return render_template('weather.html', weather=weather)
        except:
            error_message = weather_data['message']
            return render_template('weather.html', error=error_message)
    return render_template('weather.html')

def find_best_cards(user_spending, card_data):
    # max_rewards = {category: ('', 0) for category in user_spending}  # Tracks best card per category
    
    # # Calculate maximum rewards for each category
    # for card in card_data:
    #     for category, spending in user_spending.items():
    #         rewards = spending * card['rewards'][category] / 100  # Convert percentage to multiplier
    #         if rewards > max_rewards[category][1]:
    #             max_rewards[category] = (card['name'], rewards)
    
    # return max_rewards
    best_combination = []
    max_total_rewards = 0
    
    # Iterate over all possible combinations of cards
    for r in range(1, len(card_data) + 1):
        for combo in combinations(card_data, r):
            total_rewards = 0
            
            # Calculate total rewards for this combination
            for category, spending in user_spending.items():
                category_rewards = max(spending * card['rewards'][category] / 100 for card in combo)
                total_rewards += category_rewards
            
            # Update the best combination if this one has higher total rewards
            if total_rewards > max_total_rewards:
                best_combination = combo
                max_total_rewards = total_rewards
    
    # Format the result
    best_combination_result = {}
    for category in user_spending:
        best_combination_result[category] = []
        for card in best_combination:
            rewards = user_spending[category] * card['rewards'][category] / 100
            if rewards > 0:
                best_combination_result[category].append((card['name'], rewards))
    
    return best_combination_result

def get_cc_user_input():
    categories = {
        'restaurants': 'Enter your planned spending on restaurants: ',
        'grocery': 'Enter your planned spending on groceries: ',
        'flights': 'Enter your planned spending on flights: ',
        'hotel': 'Enter your planned spending on hotels: ',
        'streaming': 'Enter your planned spending on streaming services: ',
        'everything_else': 'Enter your planned spending on everything else: '
    }
    user_spending = {}
    for category, message in categories.items():
        while True:
            try:
                spending_input = input(message)  # Capture input as a string
                spending = Decimal(spending_input)  # Convert string to Decimal
                if spending < 0:
                    raise ValueError("Please enter a non-negative number.")
                user_spending[category] = spending
                break  # Exit the loop if the conversion was successful
            except ValueError as e:
                print(f"Invalid input, please enter a numeric value. Error: {e}")
    return user_spending

def get_db_user(conn):
    """Function to get the current database user."""
    cur = conn.cursor()
    cur.execute("SELECT current_user;")
    user = cur.fetchone()[0]
    app.logger.info(f'Current role being leveraged {user}')
    cur.close()
    return user


def get_card_data():
    """ Retrieve credit card reward data from the PostgreSQL database. """
    conn = connect_to_db('cc_info', 'cc_user')
    get_db_user(conn)
    card_data = []
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT c.card_id, c.card_name, f.restaurants, f.grocery, f.flights, f.hotel, f.streaming, f.everything_else_rewards
            FROM dim_credit_cards c
            JOIN fact_cashback f ON c.card_id = f.card_id;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                card_data.append({
                    'name': row[1],
                    'rewards': {
                        'restaurants': row[2],
                        'grocery': row[3],
                        'flights': row[4],
                        'hotel': row[5],
                        'streaming': row[6],
                        'everything_else': row[7]
                    }
                })
        print(card_data)
    except psycopg2.Error as e:
        print("Error while fetching data from PostgreSQL:", e)
    finally:
        conn.close()
    return card_data

def calculate_best_card(user_spending):
    """Calculate the best credit card based on user spending."""
    card_data = get_card_data()  # Assumed to fetch data structured as described previously
    best_card = None
    max_reward = Decimal('-1')  # Use Decimal for initialization of max_reward


    # Iterate over each card in the dataset
    for card in card_data:
        # Log each reward calculation for debugging (optional, can be removed for production)
        for category in user_spending:
            app.logger.info(f"Rewards for {category} using {card['name']}: {card['rewards'].get(category, Decimal('0.0'))}, Spending: {user_spending[category]}")
        
        # Calculate the total rewards for this card based on user spending and card rewards rates
        total_rewards = sum(
            user_spending[category] * (card['rewards'].get(category, Decimal('0.0')) / Decimal('100.0'))
            for category in user_spending
        )

        # Check if this card offers the highest total rewards so far
        if total_rewards > max_reward:
            best_card = card
            max_reward = total_rewards

    return best_card

@app.route('/credit_cards', methods=['GET', 'POST'])
def credit_card_info():
    app.logger.info(f'Received a {request.method} request')
    if request.method == 'POST':
        # Extract form data
        user_spending = {
        'restaurants': Decimal(request.form['restaurants']),
        'grocery': Decimal(request.form['grocery']),
        'flights': Decimal(request.form['flights']),
        'hotel': Decimal(request.form['hotel']),
        'streaming': Decimal(request.form['streaming']),
        'everything_else': Decimal(request.form['everything_else'])
    }
        app.logger.info(user_spending)
        # Process the data to find the best card (implementation dependent)
        best_card = calculate_best_card(user_spending)
        app.logger.info(best_card)
        # Render the results template with the best card info
        return render_template('cc_results.html', best_card=best_card, user_spending=user_spending)

    # Render the index page if method is GET or no form has been submitted
    return render_template('cc.html')


if __name__ == "__main__":
    app.logger.setLevel(logging.INFO)
    app.run(host="0.0.0.0", debug=True, port="8000")