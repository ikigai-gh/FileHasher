from flask import Flask, request, Response
from celery import chain, current_app
from celery.exceptions import TimeoutError

from celery_conf import make_celery
import json

from utils import compute_md5, download_file, send_email as email

flask_app = Flask(__name__)

flask_app.config['EMAIL_HOST'] = 'smtp.gmail.com'
flask_app.config['EMAIL_PORT'] = 587
flask_app.config['EMAIL_USE_TLS'] = True
flask_app.config['EMAIL_HOST_USER'] = ''
flask_app.config['EMAIL_HOST_PASSWORD'] = ''
flask_app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
flask_app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

flask_app.app_context()

celery_app = make_celery(flask_app)


@celery_app.task
def calc_file_md5(url):
    result = {'url': url, 'md5': compute_md5(download_file(url))}
    return result


@celery_app.task
def send_email(self, mail_to, mail_from):
    url = self['url']
    md5 = self['md5']
    email(mail_to, mail_from, (url, md5))


@flask_app.route('/submit', methods=['POST'])
def submit():
    url = request.form.get('url')
    email_ = request.form.get('email')
    task_info = {}

    if url:
        if email_:
            task_info['id'] = chain(calc_file_md5.s(url), send_email.s(('foo', email_), ('foo', flask_app.config['EMAIL_HOST_USER'])))().parent.id
        else:
            task_info['id'] = calc_file_md5.delay(url).id
        return Response(json.dumps(task_info), status=201)
    else:
        return Response(json.dumps({'error': 'Url was not provided'}), status=400)


@flask_app.route('/check', methods=['GET'])
def check():
    task_id = request.args.get('id')

    if task_id:
        try:
            task = calc_file_md5.AsyncResult(task_id).get(timeout=0.1)
        except TimeoutError:
            task = None
        if task:
            if calc_file_md5.AsyncResult(task_id).ready():
                status = 500 if calc_file_md5.AsyncResult(task_id).failed() else 200
                resp = Response(json.dumps({'status': calc_file_md5.AsyncResult(task_id).status, **calc_file_md5.AsyncResult(task_id).result}), status=status)
            else:
                resp = Response(json.dumps({'status': calc_file_md5.AsyncResult(task_id).status}), status=206)
        else:
            resp = Response(json.dumps({'error': 'Task does not exist'}), status=404)
    else:
        resp = Response(json.dumps({'error': 'Task id was not provided'}), status=400)
    return resp


if __name__ == '__main__':
    flask_app.run()
