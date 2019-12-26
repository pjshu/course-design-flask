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
        except Exception as e:
            db.session.rollback()
            raise


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
        blacklist = ["id", "student_id"]
        change = ['punish', 'change', 'reward']
        for key, value in attrs.items():
            if not value:
                continue
            if key in change and value['level']:
                model = models[key]
                m = model.query.filter_by(student_id=self.id).first() or model()
                value['student_id'] = self.id
                m.set_attrs(value)
                m.auto_commit()
                continue
            if hasattr(self, key) and key not in blacklist:
                setattr(self, key, value)
        self.auto_commit()

    @property
    def birthday_(self):
        return time.strftime("%Y-%m-%d", time.localtime(self.birthday))

    def _query_state(self, model):
        m = model.query.filter_by(student_id=self.id).first()
        if not m:
            return {
                "level": '',
                "description": '',
            }
        return {
            "level": m.level or '',
            "description": m.description,
        }

    @property
    def detail(self):
        c = self.class_department()
        return {
            "id": self.id,
            "name": self.name,
            "sex": self.sex,
            "birthday": self.birthday_,
            "native_place": self.native_place,
            "classes": c['classes'],
            "department": c['department'],
            "change": self._query_state(Change),
            "punish": self._query_state(Punishment),
            "reward": self._query_state(Reward),
            "monitor": self.is_monitor(),
        }

    def class_department(self):
        class_ = Class.query.get(self.class_id)
        department = Department.query.get(class_.department_id)
        return {
            "classes": {"id": class_.id, "name": class_.name},
            "department": {"id": department.id, "name": department.name}
        }

    def is_monitor(self):
        return Class.query.get(self.class_id).monitor == self.id


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

    def set_attrs(self, attrs: dict):
        self.rec_tim = int(time.time())
        setattr(self, 'description', attrs['description'])
        setattr(self, 'level_id', self.query_level_id(attrs['level']))
        setattr(self, 'student_id', attrs['student_id'])

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
        levels = cls.query.all()
        return [{"code": level.code, "description": level.description} for level in levels]


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
