import pytest
from sqlalchemy import event

from .. import create_app, db as _db


@pytest.fixture(scope="session")
def app(request):
    return create_app("testing")


@pytest.fixture(scope="session")
def db(app, request):
    with app.app_context():
        # _db.drop_all()
        # _db.create_all()
        pass


@pytest.fixture(scope="session", autouse=True)
def session(app, db, request):
    with app.app_context():
        conn = _db.engine.connect()
        txn = conn.begin()

        options = dict(bind=conn, binds={})
        sess = _db.create_scoped_session(options=options)

        sess.begin_nested()

        @event.listens_for(sess(), 'after_transaction_end')
        def restart_savepoint(sess2, trans):
            if trans.nested and not trans._parent.nested:
                sess2.expire_all()
                sess.begin_nested()

        _db.session = sess
        yield sess

        sess.remove()
        txn.rollback()
        conn.close()

