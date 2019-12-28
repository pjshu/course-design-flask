from .. import db
from functools import partial

NullColumn = partial(db.Column, nullable=True)


class Base(db.Model):
    __abstract__ = True

    def auto_commit(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise
