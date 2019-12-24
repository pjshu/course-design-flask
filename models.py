import time
from functools import partial

from . import db

NullColumn = partial(db.Column, nullable=True)


class Base(db.Model):
    __abstract__ = True

    def auto_commit(self):
        db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()


# 学生个人信息表
class Student(Base):
    __tablename__ = 'STUDENT'
    id = NullColumn('ID', db.Integer, primary_key=True)
    name = NullColumn('NAME', db.String(128))
    # mysql 不支持检查约束? 手动维护完整性
    sex = NullColumn('SEX', db.String(128))
    birthday = NullColumn('BIRTHDAY', db.Integer)
    native_place = NullColumn('NATIVE_PLACE', db.String(128))

    class_id = NullColumn('CLASS', db.Integer, db.ForeignKey('CLASS.ID'))

    def set_attrs(self, attrs: dict):
        blacklist = ["id", 'class_id']
        for key, value in attrs.items():
            if hasattr(self, key) and key not in blacklist:
                setattr(self, key, value)

    @property
    def _birthday(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.birthday))

    def _query_state(self, model):
        m = model.query.filter_by(student_id=self.id).first()
        if not m:
            return False
        return m.change_description

    @property
    def punish(self):
        return self._query_state(Punishment)

    @property
    def reward(self):
        return self._query_state(Reward)

    @property
    def change(self):
        return self._query_state(Change)

    @property
    def detail(self):
        return {
            "id": self.id,
            "name": self.name,
            "sex": self.sex,
            "birthday": self._birthday,
            "native_place": self.native_place,
            "change": self.change,
            "punish": self.punish,
            "reward": self.reward
        }


# 院系信息表
class Department(Base):
    __tablename__ = 'DEPARTMENT'
    id = NullColumn('ID', db.Integer, primary_key=True)
    name = NullColumn('NAME', db.String(128))

    classes = db.relationship('Class', backref='DEPARTMENT', lazy='dynamic')

    def set_attrs(self, attrs: dict):
        blacklist = ["id", 'class_']
        for key, value in attrs.items():
            if hasattr(self, key) and key not in blacklist:
                setattr(self, key, value)
            if key == 'class':
                self.class_.append(key)


# 班级信息表
class Class(Base):
    __tablename__ = 'CLASS'
    id = NullColumn('ID', db.Integer, primary_key=True)
    name = NullColumn('NAME', db.String(128))
    monitor = NullColumn('MONITOR', db.Integer)

    department_id = db.Column(db.Integer, db.ForeignKey('DEPARTMENT.ID'))
    student = db.relationship('Student', backref='CLASS', lazy='dynamic')

    # 修改班级时先删除班级学生
    def add_student(self, student):
        for s in self.student:
            if s.id == student.id:
                self.student.remove(s)
                break
        self.student.append(student)


class BaseChange(Base):
    __abstract__ = True
    id = NullColumn('ID', db.Integer, primary_key=True)
    rec_tim = NullColumn('REC_TIM', db.Integer)
    description = NullColumn('DESCRIPTION', db.Text)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rec_tim = int(time.time())

    def set_attrs(self, attrs: dict):
        blacklist = ["id", "rec_tim", 'description']
        for key, value in attrs.items():
            if hasattr(self, key) and key not in blacklist:
                setattr(self, key, value)


# 学籍变更信息表
class Change(BaseChange):
    __tablename__ = 'CHANGE'
    student_id = NullColumn('STUDENTID', db.Integer, db.ForeignKey('STUDENT.ID'))
    levels = NullColumn('CHANGE', db.Integer, db.ForeignKey('CHANGE_CODE.CODE'))

    @property
    def change_description(self):
        return Change_code.query.get(self.levels).description


# 奖励记录信息表
class Reward(BaseChange):
    __tablename__ = 'REWARD'
    student_id = NullColumn('STUDENTID', db.Integer, db.ForeignKey('STUDENT.ID'))
    levels = NullColumn('LEVELS', db.Integer, db.ForeignKey('REWARD_LEVELS.CODE'))

    @property
    def change_description(self):
        return Reward_levels.query.get(self.levels).description


# 处罚记录信息表
class Punishment(BaseChange):
    __tablename__ = 'PUNISHMENT'
    student_id = NullColumn('STUDENTID', db.Integer, db.ForeignKey('STUDENT.ID'))
    levels = NullColumn('LEVELS', db.Integer, db.ForeignKey('PUBLISH_LEVELS.CODE'))

    @property
    def change_description(self):
        return Publish_levels.query.get(self.levels).description

    @property
    def enable(self):
        return self.levels != 0


class BaseLevel(Base):
    __abstract__ = True
    code = NullColumn('CODE', db.Integer, primary_key=True, autoincrement=False)
    description = NullColumn('DESCRIPTION', db.Text)

    def __init__(self, code, description):
        self.description = description
        self.code = code

    @classmethod
    def all(cls):
        return cls.query.all()


# 学籍变动代码表
class Change_code(BaseLevel):
    __tablename__ = 'CHANGE_CODE'

    def __init__(self, code, description):
        super().__init__(code, description)


# 奖励等级代码表
class Reward_levels(BaseLevel):
    __tablename__ = 'REWARD_LEVELS'

    def __init__(self, code, description):
        super().__init__(code, description)


# 惩罚等级代码表
class Publish_levels(BaseLevel):
    __tablename__ = 'PUBLISH_LEVELS'

    def __init__(self, code, description):
        super().__init__(code, description)


organizations = {
    "department": lambda _: Department.query.all(),
    "class": lambda cid: Department.query.get(int(cid)).classes,
    "student": lambda sid: Class.query.get(int(sid)).student
}

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
