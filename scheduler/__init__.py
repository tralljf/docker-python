from flask import Flask, jsonify, request
from celery import Celery
from datetime import timedelta

import pymysql.cursors
import requests
import json


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


app = Flask(__name__)
app.config['CELERY_BACKEND'] = "redis://redis:6379/0"
app.config['CELERY_BROKER_URL'] = "redis://redis:6379/0"

app.config['CELERYBEAT_SCHEDULE'] = {
    'say-every-5-seconds': {
        'task': 'price',
        'schedule': timedelta(seconds=5)
    },
}


app.config['CELERY_TIMEZONE'] = 'UTC'
celery_app = make_celery(app)


@celery_app.task(name='price')
# def return_something():
#     print ('something')
#     return 'something'
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

  except Exception as e:
    print(e)
    return jsonify([{
      'error': 'Ocorreu um erro'
    }])
