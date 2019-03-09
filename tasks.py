from celery import Celery

from celery_conf import make_celery
from utils import compute_md5, download_file, send_email as email

app = make_celery()


@app.task
def calc_file_md5(url):
    compute_md5(download_file(url))
    return calc_file_md5.request.id


@app.task
def send_email(mail_to, mail_from, payload):
    email(mail_to, mail_from, payload)
    return send_email.request.id
