echo "** Creating CC Info"

psql -v ON_ERROR_STOP=1  <<-EOSQL
    CREATE DATABASE cc_info;
    CREATE USER cc_user WITH PASSWORD '$POSTGRES_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE cc_info TO cc_user;
EOSQL

psql -d cc_info -v ON_ERROR_STOP=1  <<-EOSQL
    CREATE TABLE dim_credit_cards (
    card_id INT PRIMARY KEY,  -- Unique identifier for each card
    card_name VARCHAR(255),
    bank VARCHAR(255)
);

    CREATE TABLE fact_cashback (
    card_id INT,  -- FK to dim_credit_cards
    restaurants DECIMAL(5,4),
    grocery DECIMAL(5,4),
    flights DECIMAL(5,4),
    hotel DECIMAL(5,4),
    streaming DECIMAL(5,4),
    everything_else_rewards DECIMAL(5,4),
    annual_fee DECIMAL(10, 2)
);
    CREATE TABLE dim_additional_rewards (
    card_id INT,  -- FK to dim_credit_cards
    tsa_precheck BOOLEAN,
    additional_rewards DECIMAL(10,2)
);

    ALTER TABLE fact_cashback
    ADD CONSTRAINT fact_cashback_card_id
    FOREIGN KEY (card_id) REFERENCES dim_credit_cards(card_id);

    ALTER TABLE dim_additional_rewards
    ADD CONSTRAINT fk_additional_rewards_card_id
    FOREIGN KEY (card_id) REFERENCES dim_credit_cards(card_id);

    INSERT INTO dim_credit_cards (card_id, card_name, bank) VALUES
    (1, 'Barclays', 'Barclays'),
    (2, 'Quicksilver', 'Capital One'),
    (3, 'Savor One', 'Capital One'),
    (4, 'CSP', 'Chase'),
    (5, 'AMEX Gold', 'American Express'),
    (6, 'Venture X', 'Capital One'),
    (7, 'CSR', 'Chase'),
    (8, 'Marriott Bountiful', 'Marriott'),
    (9, 'AMEX Platinum', 'American Express'),
    (10, 'Robinhood Gold', 'Robinhood'),
    (11, 'Chase Flex', 'Chase');

    INSERT INTO fact_cashback (card_id, restaurants, grocery, flights, hotel, streaming, everything_else_rewards, annual_fee) VALUES
    (1, 0.03, 0.02, 0.01, 0.01, 0.02, 0.01, 0.00),
    (2, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.00),
    (3, 0.03, 0.03, 0.01, 0.01, 0.03, 0.01, 0.00),
    (4, 0.03, 0.03, 0.05, 0.05, 0.03, 0.01, 95.00),
    (5, 0.04, 0.04, 0.03, 0.01, 0.01, 0.01, 250.00),
    (6, 0.02, 0.02, 0.08, 0.08, 0.02, 0.02, 395.00),
    (7, 0.01, 0.01, 0.08, 0.08, 0.01, 0.01, 550.00),
    (8, 0.04, 0.04, 0.06, 0.06, 0.02, 0.02, 250.00),
    (9, 0.01, 0.01, 0.05, 0.05, 0.01, 0.01, 695.00),
    (10, 0.03, 0.03, 0.05, 0.05, 0.03, 0.03, 60.00),
    (11, 0.01, 0.01, 0.05, 0.05, 0.01, 0.01, 0.00);


    INSERT INTO dim_additional_rewards (card_id, tsa_precheck, additional_rewards) VALUES
    (6, TRUE, 400.00),
    (7, TRUE, 400.00),
    (9, TRUE, 300.00),
    (5, FALSE, 220.00),
    (8, FALSE, 300.00);

EOSQL

psql -d cc_info -v ON_ERROR_STOP=1  <<-EOSQL
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cc_user;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO cc_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cc_user;
EOSQL

echo "** Finished CC"