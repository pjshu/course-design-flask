import time

from flask import request

from .blueprint import api
from .utils import generate_res
from ..models import Student, Class


# 录入
@api.route('/record/', methods=["POST"])
def record():
    data = request.get_json()
    class_id = data.get('class_id')
    class_ = Class.query.get(int(class_id or -1))
    sex = data.get('sex')
    if not class_ or sex not in ['男', '女']:
        return generate_res("failed")
    student = Student()
    student.set_attrs(data)
    class_.add_student(student)
    class_.auto_commit()
    return generate_res("success")
