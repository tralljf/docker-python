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
    print('aqui')
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

