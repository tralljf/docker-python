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

# app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'

celery = Celery(app.name, broker=app.config['CACHE_REDIS_URL'])
celery.conf.update(app.config)

CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'task_teste',
        'schedule': timedelta(seconds=10)
    },
}

@celery.task
def task_teste():
    with app.app_context():
        print('running my task')

# task = task_teste.apply_async()
# # cache = Cache(app)  


@app.route('/price', methods=['GET'])
def price():
  try:
    max_value = 10000
    exchange = 'Bitpreco'
    url = "https://api.bitpreco.com/btc-brl/orderbook"
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers)

    sell_rate = 0
    buy_rate = 0
    total_satisfied = 0
    sell_book = ""
    rJson = json.loads(response.text)
    for bid in rJson['bids']:       
        sell_book = "{}{:.8f}:{:.2f};".format(sell_book, float(bid['amount']), float(bid['price']))
        satisfied_this_order = float(bid['amount']) * float(bid['price'])
        total_satisfied = total_satisfied + satisfied_this_order
        if total_satisfied >= max_value:
            sell_rate = float("{0:.2f}".format(bid['price']))
            break
    buy_book = ""
    total_satisfied = 0
    for ask in rJson['asks']:
        buy_book = "{}{:.8f}:{:.2f};".format(buy_book, float(ask['amount']), float(ask['price']))                         
        satisfied_this_order = float(ask['amount']) * float(ask['price'])
        total_satisfied = total_satisfied + satisfied_this_order
        if total_satisfied >= max_value:
            buy_rate = float("{0:.2f}".format(ask['price']))
            break

    connection = pymysql.connect(host='db',
                             user='root',
                             password='root',
                             database='crypto',
                             cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # Create a new record
            
            sql = "INSERT INTO `PRICES` (`sell_rate`, `buy_rate`, `sell_book`, `buy_book`, `exchange`) VALUES ({}, {}, '{}', '{}', '{}')".format(sell_rate, buy_rate, sell_book, buy_book, exchange)
            print(sql)
            cursor.execute(sql)

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

    # with connection.cursor() as cursor:
    #     # Read a single record
    #     sql = "SELECT `sell_rate`, `buy_rate`, `sell_book`, `buy_book` FROM `prices` WHERE `sell_rate`=%d"
    #     cursor.execute(sql, (1,))
    #     result = cursor.fetchone()
    #     print(result)
            
    return jsonify([{
      'sell_rate2': sell_rate, 
      'buy_rate': buy_rate, 
      'sell_book': sell_book, 
      'buy_book': buy_book
    }])
  except Exception as e:
    print(e)
    return jsonify([{
      'error': 'Ocorreu um erro'
    }])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

