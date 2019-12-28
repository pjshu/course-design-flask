from . import create_app, db
from .init import init


app = create_app()

if __name__ == '__main__':
    app.run()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, create=db.create_all, drop=db.drop_all, init=init)
