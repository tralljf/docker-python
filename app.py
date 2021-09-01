from flask import Flask, jsonify, request
from flask_caching import Cache 
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

import pymysql.cursors
import requests
import json

app = Flask(__name__)
app.config.from_object('config.Config')  # Set the configuration variables to the flask application

@app.route('/price', methods=['GET'])
def price():
  try:
    connection = pymysql.connect(host='db',
                             user='root',
                             password='root',
                             database='crypto',
                             cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT `sell_book`, `buy_book` FROM `prices` order by created_at desc limit 1 "
        cursor.execute(sql)
        result = cursor.fetchone()

            
    return jsonify(result)
  except Exception as e:
    print(e)
    return jsonify([{
      'error': 'Ocorreu um erro'
    }])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

