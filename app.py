import sys
from flask import Flask, render_template

# setting path
from lib.dataset_collector import request_handler, response_handler
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
        return render_template('templates/blocked.html')

    return render_template('templates/home.html')


@app.route('/product')
@protected_endpoint
def product(blocked: bool):
    if blocked:
        return render_template('templates/blocked.html')

    return render_template('templates/product.html')


if __name__ == '__main__':
    app.run('0.0.0.0')
