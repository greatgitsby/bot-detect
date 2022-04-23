from flask import Flask, render_template
from lib import protected_endpoint

app = Flask(__name__,
            static_url_path='',
            static_folder='static/',
            template_folder='templates/')


@app.route('/home')
@protected_endpoint
def home(blocked: bool):
    return render_template('home.html', blocked=blocked)


@app.route('/product')
@protected_endpoint
def product(blocked: bool):
    return render_template('product.html', blocked=blocked)


if __name__ == '__main__':
    app.run('0.0.0.0', port=3000)
