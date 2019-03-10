from flask import Flask, request, jsonify
from celery import chain
from celery_conf import make_celery

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
    return url, compute_md5(download_file(url)), calc_file_md5.request.id


@celery_app.task
def send_email(self, mail_to, mail_from):
    url, md5 = self[:2]
    email(mail_to, mail_from, (url, md5))


@flask_app.route('/submit', methods=['POST'])
def submit():
    url = request.form.get('url')
    email_ = request.form.get('email')
    task_info = {}

    if url:
        if email:
            task_info['id'] = chain(calc_file_md5.s(url), send_email.s(('foo', email_), ('foo', flask_app.config['EMAIL_HOST_USER'])))().parent.id
        else:
            task_info['id'] = calc_file_md5.delay(url).id
        return jsonify(task_info)
    else:
        return 'Invalid request'


if __name__ == '__main__':
    flask_app.run()
