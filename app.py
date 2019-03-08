from flask import Flask, request

from tasks import calc_file_md5

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

#  TODO: Add an email sending
@app.route('/submit', methods=['POST'])
def submit():
    url = request.form.get('url')

    if url:
        return calc_file_md5.delay(url).id
    return 'Invalid request'


if __name__ == '__main__':
    app.run()
