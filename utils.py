import requests
import hashlib
from flask_emails import Message


def download_file(url):
    file_name = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=16384):
                if chunk:
                    f.write(chunk)
    return file_name


def compute_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()


def send_email(mail_to, mail_from, payload):
    html = f'<html><p>{payload}</p></html>'
    msg = Message(html=html, subject='MD5', mail_from=mail_from, mail_to=mail_to)
    resp = msg.send()

    if resp.status_code not in (250, ):
        raise ValueError('Email was not sent correctly')
