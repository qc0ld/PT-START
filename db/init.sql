CREATE USER ${DB_REPL_USER} WITH REPLICATION ENCRYPTED PASSWORD '${DB_REPL_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${DB_DATABASE} TO ${DB_REPL_USER};

SELECT pg_create_physical_replication_slot('replication_slot');

\connect ${DB_DATABASE};

CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS phone_numbers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL
);

INSERT INTO emails (email) VALUES
    ('test1@ya.ru'),     
    ('test2@ya.ru'),
    ('test3@ya.ru');

INSERT INTO phone_numbers (phone_number) VALUES
    ('81234567890'),
    ('81112223344'),
    ('81231231212');
