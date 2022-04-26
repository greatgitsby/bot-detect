import sys
from flask import Flask, render_template, request

# setting path
from lib.dataset_collector import request_handler, response_handler, get_request_log, get_db
from lib.protect import protected_endpoint

app = Flask(__name__,
            static_url_path='',
            static_folder='static/',
            template_folder='templates/')

app.secret_key = "bawtprotection"


# Register the data collector
@app.before_request(request_handler)
@app.after_request(response_handler)
@app.route('/')
@app.route('/home')
@protected_endpoint
def home(blocked: bool):
    if blocked:
        return render_template('blocked.html')

    return render_template('home.html')


@app.route('/product')
@protected_endpoint
def product(blocked: bool):
    if blocked:
        return render_template('blocked.html')

    return render_template('product.html')

@app.route("/rows")
def rows():
    request_log = get_request_log()
    return { 'log': request_log.to_dict(orient='records') }


if __name__ == '__main__':
    app.run('0.0.0.0', port=3000)
