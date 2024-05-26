FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY ./backend_app.py ./
COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

EXPOSE 8080

ENV FLASK_APP=backend_app.py
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]