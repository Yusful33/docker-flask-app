# Weather Application
This Python script is a simple weather application that retrieves weather data from the OpenWeatherMap API and stores it in a PostgreSQL database.

### Requirements
Python 3.x
Flask
Requests
Psycopg2
Docker


### Installation
1. Clone this repository to your local machine:


git clone <repository_url>

Install the required Python packages using pip:


pip install -r requirements.txt

2. Set up your PostgreSQL database with the following schema:

Copy code
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    date DATE,
    time TIME,
    city VARCHAR(255),
    temperature FLOAT,
    description TEXT
);

## Configuration
Obtain an API key from OpenWeatherMap and store it securely. Set up a Docker secret or environment variable named api-key with your API key.
Set up a Docker secret or environment variable named POSTGRES_PASSWORD with your PostgreSQL database password.
Usage
To run the application:


python app.py
The application will be accessible at http://localhost:8000.

## Usage with Docker
Alternatively, you can run the application using Docker. Make sure you have Docker installed on your system.

1. Build the Docker image:

docker build -t weather-app .
Run the Docker container:


2. docker run -p 8000:8000 --name weather-container weather-app
The application will be accessible at http://localhost:8000.

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.