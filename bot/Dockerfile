FROM python:3.10-alpine

COPY . /bot
WORKDIR /bot

RUN mkdir -p logs && \
	pip install --upgrade pip && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    apk add --no-cache postgresql-client && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    python3 -m pip install python-dotenv --no-cache-dir && \
    apk del .build-deps

CMD ["python", "bot.py"]
