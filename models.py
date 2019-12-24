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
        change = ['punish', 'change', 'reward']
        for key, value in attrs.items():
            if key in change:
                model = models[key]
                m = model.query.filter_by(student_id=int(self.id)).first() or model()
                value['student_id'] = self.id
                m.set_attrs(value)
                m.auto_commit()
                continue
            if hasattr(self, key) and key not in blacklist:
                setattr(self, key, value)

    @property
    def _birthday(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.birthday))

    def _query_state(self, model):
        m = model.query.filter_by(student_id=self.id).first()
        if not m:
            return False
        return {
            "level_code": m.level_id,
            "level": m.level,
            "description": m.description,
        }

    @property
    def detail(self):
        return {
            "id": self.id,
            "name": self.name,
            "sex": self.sex,
            "birthday": self._birthday,
            "native_place": self.native_place,
            "change": self._query_state(Punishment),
            "punish": self._query_state(Reward),
            "reward": self._query_state(Change)
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
        blacklist = ["id", "rec_tim"]
        for key, value in attrs.items():
            if hasattr(self, key) and key not in blacklist:
                setattr(self, key, value)


# 学籍变更信息表
class Change(BaseChange):
    __tablename__ = 'CHANGE'
    student_id = NullColumn('STUDENTID', db.Integer, db.ForeignKey('STUDENT.ID'))
    level_id = NullColumn('CHANGE', db.Integer, db.ForeignKey('CHANGE_CODE.CODE'))

    @property
    def level(self):
        return Change_code.query.get(self.level_id).description


# 奖励记录信息表
class Reward(BaseChange):
    __tablename__ = 'REWARD'
    student_id = NullColumn('STUDENTID', db.Integer, db.ForeignKey('STUDENT.ID'))
    level_id = NullColumn('LEVELS', db.Integer, db.ForeignKey('REWARD_LEVELS.CODE'))

    @property
    def level(self):
        return Reward_levels.query.get(self.level_id).description


# 处罚记录信息表
class Punishment(BaseChange):
    __tablename__ = 'PUNISHMENT'
    student_id = NullColumn('STUDENTID', db.Integer, db.ForeignKey('STUDENT.ID'))
    level_id = NullColumn('LEVELS', db.Integer, db.ForeignKey('PUBLISH_LEVELS.CODE'))

    @property
    def level(self):
        return Publish_levels.query.get(self.level_id).description

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
        levels = cls.query.all()
        return [{"code": level.code, "description": level.description} for level in levels]


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
