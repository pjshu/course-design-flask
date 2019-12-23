from flask import render_template

from .blueprint import main


@main.route('/', defaults={'path': ''})
@main.route('/<path:path>')
def home(path):
    return render_template('index.html')


