## FileHasher

### Instructions for run:
```bash
sudo apt install redis
sudo systemctl start redis
cd FileHasher
virtualenv env
source env/bin/activate
pip install -r requirements.txt
celery -A app worker --loglevel=info
python -m flask run
```