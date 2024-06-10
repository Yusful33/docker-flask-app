# -- Create database if it does not exist
# CREATE DATABASE weather_info;


# -- Create user if it does not exist
# CREATE USER weather_user WITH PASSWORD '${POSTGRES_PASSWORD}';


echo "** Creating  DB and user"

psql -v ON_ERROR_STOP=1  <<-EOSQL
    CREATE DATABASE weather_info;
    CREATE USER weather_user WITH PASSWORD '$POSTGRES_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE weather_info TO weather_user;
    CREATE TABLE IF NOT EXISTS weather_data (
                      id SERIAL PRIMARY KEY,
                      date DATE,
                      time TIME,
                      city VARCHAR(255),
                      temperature FLOAT,
                      description TEXT
                      )
EOSQL

echo "** Finished creating  DB and user"


