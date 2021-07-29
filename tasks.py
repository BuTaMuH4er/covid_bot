from celery import Celery
from datetime import datetime

celery_app = Celery('covidla_tasks',broker='redis://localhost:6379/0')

@celery_app.task
def what_time():
    print(datetime.now())
