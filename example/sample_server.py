from flask import Flask, render_template
from lib import protected_endpoint

app = Flask(__name__,
            static_url_path='',
            static_folder='static/',
            template_folder='templates/')

app.secret_key = "bawtprotection"


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


if __name__ == '__main__':
    app.run('0.0.0.0', port=3000)
