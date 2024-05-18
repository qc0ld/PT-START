DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'DB_DATABASE') THEN
        EXECUTE 'CREATE DATABASE DB_DATABASE';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'DB_REPL_USER') THEN
        EXECUTE 'CREATE USER DB_REPL_USER WITH REPLICATION ENCRYPTED PASSWORD ''DB_REPL_PASSWORD''';
    END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE DB_DATABASE TO DB_REPL_USER;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replication_slot') THEN
        PERFORM pg_create_physical_replication_slot('replication_slot');
    END IF;
END
$$;

\connect DB_DATABASE;

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
    ('test3@ya.ru')
ON CONFLICT DO NOTHING;

INSERT INTO phone_numbers (phone_number) VALUES
    ('81234567890'),
    ('81112223344'),
    ('81231231212')
ON CONFLICT DO NOTHING;
