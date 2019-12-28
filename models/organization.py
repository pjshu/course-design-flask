import time

from .base import NullColumn, Base
from .change import models
from .. import db


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
                continue
            if hasattr(self, key) and key not in blacklist:
                setattr(self, key, value)
        self.auto_commit()

    @property
    def birthday_(self):
        return time.strftime("%Y-%m-%d", time.localtime(self.birthday))

    def _query_state(self, model):
        m = model.query.filter_by(student_id=self.id).first() or {}

        return {
            "level": getattr(m, 'level', ''),
            "description": getattr(m, 'description', ''),
        }

    @property
    def detail(self):
        c = self.class_department
        return {
            "id": self.id,
            "name": self.name,
            "sex": self.sex,
            "birthday": self.birthday_,
            "native_place": self.native_place,
            "classes": c['classes'],
            "department": c['department'],
            "change": self._query_state(models['change']),
            "punish": self._query_state(models['punish']),
            "reward": self._query_state(models['reward']),
            "monitor": self.is_monitor,
        }

    @property
    def class_department(self):
        class_ = Class.query.get(self.class_id)
        department = Department.query.get(class_.department_id)
        return {
            "classes": {"id": class_.id, "name": class_.name},
            "department": {"id": department.id, "name": department.name}
        }

    @property
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
