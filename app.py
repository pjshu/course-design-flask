from . import create_app
from .init import init
from .models import db
from flask_cors import CORS

app = create_app()
CORS(app)

if __name__ == '__main__':
    app.run()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, create=db.create_all, drop=db.drop_all, init=init)
