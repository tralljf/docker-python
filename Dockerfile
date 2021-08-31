FROM python:3.8-slim-buster

EXPOSE 5000

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Run app.py when the container launches
COPY . .