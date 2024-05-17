FROM postgres:latest

ARG DB_HOST
ARG DB_NAME
ARG DB_DATABASE
ARG DB_REPL_PORT
ARG DB_REPL_USER
ARG DB_REPL_PASSWORD

RUN echo "#!/bin/bash" > /init.sh && \
    echo "rm -rf /var/lib/postgresql/data/*" >> /init.sh && \
    echo "until PGPASSWORD=$DB_REPL_PASSWORD pg_basebackup --pgdata=/var/lib/postgresql/data -R --slot=replication_slot --username=$DB_REPL_USER --host=$DB_HOST --port=$DB_REPL_PORT; do" >> /init.sh && \
    echo "  sleep 2" >> /init.sh && \
    echo "done" >> /init.sh && \
    echo "chmod 0700 /var/lib/postgresql/data" >> /init.sh && \
    echo "psql -h $DB_HOST -U $DB_REPL_USER -d $DB_DATABASE"  >> /init.sh && \
    echo "postgres" >> /init.sh && \
    chmod +x /init.sh

USER postgres

CMD ["/init.sh"]
