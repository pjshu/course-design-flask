from . import create_app, db
from init import init
from flask_migrate import upgrade

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, create=db.create_all, drop=db.drop_all, init=init)


@app.cli.command()
def deploy():
    upgrade()


if __name__ == '__main__':
    app.run()
