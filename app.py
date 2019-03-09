from flask import Flask, request
from celery import chain
from celery_conf import make_celery

from utils import compute_md5, download_file, send_email as email

flask_app = Flask(__name__)
# app.config['EMAIL_HOST'] = 'localhost'
# app.config['EMAIL_PORT'] = 25
# app.config['EMAIL_TIMEOUT'] = 5
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
    compute_md5(download_file(url))
    return calc_file_md5.request.id


@celery_app.task
def send_email(mail_to, mail_from, payload):
    email(mail_to, mail_from, payload)
    return send_email.request.id


#  TODO: Add an email sending
@flask_app.route('/submit', methods=['POST'])
def submit():
    url = request.form.get('url')
    email = request.form.get('email')

    if url:
        if email:
           # chain(calc_file_md5.s(url), send_email.s(('foo', 'sadmonad@gmail.com'), ('foo', 'sadmonad.trash@gmail.com'), 'anime')).apply_async()
                send_email.delay(('foo', 'sadmonad@gmail.com'), ('foo', 'sadmonad.trash@gmail.com'), 'anime')
                return 'anime'
        else:
            return calc_file_md5.delay(url).id
    return 'Invalid request'


if __name__ == '__main__':
    print(flask_app.config)
    flask_app.run()
