from celery import Celery

from utils import compute_md5, download_file

app = Celery('FileHasherTasks', broker='redis://localhost')


@app.task
def calc_file_md5(url):
    return compute_md5(download_file(url))
