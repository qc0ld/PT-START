FROM postgres:latest

COPY init.sql /init.sql

ARG DB_REPL_USER
ARG DB_REPL_PASSWORD
ARG DB_DATABASE
ARG DB_PORT

RUN apt-get update && apt-get install -y gettext-base && \
    envsubst '${DB_REPL_USER} ${DB_REPL_PASSWORD} ${DB_DATABASE}' < /init.sql > /docker-entrypoint-initdb.d/init.sql && \
    echo "listen_addresses = '*'" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "port = ${DB_PORT}" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "archive_mode = on" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "archive_command = 'cp %p /oracle/pg_data/archive/%f'" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "log_destination = 'stderr'" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "logging_collector = on" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "log_directory = '/var/log/postgresql/'" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "log_filename = 'postgresql.log'" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "max_wal_senders=10" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "wal_level=replica" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "wal_log_hints = on" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "hot_standby=on" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "max_replication_slots=10" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "hot_standby_feedback=on" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "log_replication_commands=on" >> /usr/share/postgresql/postgresql.conf.sample && \
    mkdir -p /oracle/pg_data/archive && chown -R postgres:postgres /oracle/pg_data/archive && chmod -R 700 /oracle/pg_data/archive


RUN echo "host replication all 0.0.0.0/0 md5" >> /usr/share/postgresql/16/pg_hba.conf.sample

CMD ["postgres"]
