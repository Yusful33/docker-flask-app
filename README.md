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

```
git clone <repository_url>
```

Install the required Python packages using pip:


pip install -r requirements.txt

2. Set up your PostgreSQL database with the following schema:

```
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    date DATE,
    time TIME,
    city VARCHAR(255),
    temperature FLOAT,
    description TEXT
);
```

## Configuration
Obtain an API key from OpenWeatherMap and store it securely. Set up a Docker secret or environment variable named api-key with your API key.
Set up a Docker secret or environment variable named POSTGRES_PASSWORD with your PostgreSQL database password.
Usage
To run the application:

```
python app.py
```
The application will be accessible at http://localhost:8000.

## Usage with Docker
Alternatively, you can run the application using Docker. Make sure you have Docker installed on your system.

1. Grant Executable Permission on the Host 

```
chmod +x ./cc_init.sh
chmod +x ./weather_init.sh
```

2. Leverage Docker Compose to deploy the application 

```
docker compose up --build
```


The application will be accessible at http://localhost:8000.

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.
