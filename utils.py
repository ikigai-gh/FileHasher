import requests
import hashlib


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
