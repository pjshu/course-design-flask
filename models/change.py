import time

from .base import Base, NullColumn
from .. import db


class BaseChange(Base):
    __abstract__ = True
    id = NullColumn('ID', db.Integer, primary_key=True)
    rec_tim = NullColumn('REC_TIM', db.Integer)
    description = NullColumn('DESCRIPTION', db.Text)

    def set_attrs(self, attrs: dict):
        self.rec_tim = int(time.time())
        setattr(self, 'description', attrs['description'])
        setattr(self, 'level_id', self.query_level_id(attrs['level']))
        setattr(self, 'student_id', attrs['student_id'])
        self.auto_commit()

    def query_level_id(self, description):
        m = level_models[self.level_model].query.filter_by(description=description).first()
        return m.code

    @property
    def level(self):
        des = level_models[self.level_model].query.get(self.level_id)
        return des.description if des else None


# 学籍变更信息表
class Change(BaseChange):
    __tablename__ = 'CHANGE'
    student_id = NullColumn('STUDENTID', db.Integer, db.ForeignKey('STUDENT.ID'))
    level_id = NullColumn('CHANGE', db.Integer, db.ForeignKey('CHANGE_CODE.CODE'))
    level_model = 'change'


# 奖励记录信息表
class Reward(BaseChange):
    __tablename__ = 'REWARD'
    student_id = NullColumn('STUDENTID', db.Integer, db.ForeignKey('STUDENT.ID'))
    level_id = NullColumn('LEVELS', db.Integer, db.ForeignKey('REWARD_LEVELS.CODE'))
    level_model = 'reward'


# 处罚记录信息表
class Punishment(BaseChange):
    __tablename__ = 'PUNISHMENT'
    student_id = NullColumn('STUDENTID', db.Integer, db.ForeignKey('STUDENT.ID'))
    level_id = NullColumn('LEVELS', db.Integer, db.ForeignKey('PUBLISH_LEVELS.CODE'))
    level_model = 'punish'


class BaseLevel(Base):
    __abstract__ = True
    code = NullColumn('CODE', db.Integer, primary_key=True, autoincrement=False)
    description = NullColumn('DESCRIPTION', db.Text)

    def __init__(self, code, description):
        self.description = description
        self.code = code

    @classmethod
    def all(cls):
        return [{"code": level.code, "description": level.description} for level in cls.query.all()]


# 学籍变动代码表
class Change_code(BaseLevel):
    __tablename__ = 'CHANGE_CODE'


# 奖励等级代码表
class Reward_levels(BaseLevel):
    __tablename__ = 'REWARD_LEVELS'


# 惩罚等级代码表
class Publish_levels(BaseLevel):
    __tablename__ = 'PUBLISH_LEVELS'


models = {
    "punish": Punishment,
    "reward": Reward,
    "change": Change,
}


level_models = {
    "punish": Publish_levels,
    "reward": Reward_levels,
    "change": Change_code,
}
