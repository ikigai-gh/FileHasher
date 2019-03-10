## FileHasher

### Install & start redis
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

### Presettings:
In the file `flask_conf.py` specify your own settings for email sending

### Instructions for run:
```bash
cd FileHasher
virtualenv env
source env/bin/activate
pip install -r requirements.txt
celery -A app worker --loglevel=info
python -m flask run
```
