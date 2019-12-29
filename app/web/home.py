from flask import current_app, render_template

from .blueprint import main


@main.route('/', defaults={'path': ''})
@main.route('/<path:path>')
@main.route('/students/<path:path>')
@main.route('/classes/<path:path>')
def home(path):
    return current_app.send_static_file('index.html')
