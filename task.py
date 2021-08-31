try:
    from flask import Flask
    from celery import Celery
    from datetime import timedelta
except Exception as e:
    print("Error : {} ".format(e))



app = Flask(__name__)
app.config.from_object('config.Config')
# app.config['CELERY_BACKEND'] = "redis://redis:6379/0"
# app.config['CELERY_BROKER_URL'] = "redis://redis:6379/0"

app.config['CELERYBEAT_SCHEDULE'] = {
    'say-every-5-seconds': {
        'task': 'return_something',
        'schedule': timedelta(seconds=5)
    },
}


app.config['CELERY_TIMEZONE'] = 'UTC'
# celery_app = make_celery(app)


@app.task(name='return_something')
def return_something():
    print ('something')
    return 'something'