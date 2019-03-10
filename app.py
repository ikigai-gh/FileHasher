from flask import Flask, request, Response
from celery import chain

from celery_conf import make_celery
import json

from utils import compute_md5, download_file, send_email

flask_app = Flask(__name__)
flask_app.config.from_object('flask_conf.Config')

celery_app = make_celery(flask_app)


@celery_app.task
def calc_file_md5_task(url):
    result = {'url': url, 'md5': compute_md5(download_file(url))}
    return result


@celery_app.task
def send_email_task(self, mail_to, mail_from):
    url = self['url']
    md5 = self['md5']
    send_email(mail_to, mail_from, (url, md5))


@flask_app.route('/submit', methods=['POST'])
def submit():
    url = request.form.get('url')
    email = request.form.get('email')

    task_info = {}

    mail_from = (email, email)
    mail_to = (flask_app.config['EMAIL_HOST_USER'], flask_app.config['EMAIL_HOST_USER'])

    if url:
        if email:
            task_info['id'] = chain(calc_file_md5_task.s(url), send_email_task.s(mail_to, mail_from))().parent.id
        else:
            task_info['id'] = calc_file_md5_task.delay(url).id
        return Response(json.dumps(task_info), status=201)
    else:
        return Response(json.dumps({'error': 'Url was not provided'}), status=400)


@flask_app.route('/check', methods=['GET'])
def check():
    task_id = request.args.get('id')

    if task_id:
        if calc_file_md5_task.AsyncResult(task_id).ready():
            status = 500 if calc_file_md5_task.AsyncResult(task_id).failed() else 200
            resp = Response(json.dumps({'status': calc_file_md5_task.AsyncResult(task_id).status, **calc_file_md5_task.AsyncResult(task_id).result}), status=status)
        else:
            resp = Response(json.dumps({'status': calc_file_md5_task.AsyncResult(task_id).status}), status=206)
    else:
        resp = Response(json.dumps({'error': 'Task id was not provided'}), status=400)
    return resp


if __name__ == '__main__':
    flask_app.run()
