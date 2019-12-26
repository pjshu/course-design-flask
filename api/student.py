from flask import request

from .blueprint import api
from .utils import generate_res
from ..models import Student


# 获取/修改学生信息
@api.route('/students/<sid>/', methods=['POST', "GET"])
def student(sid):
    data = request.get_json()
    stu = Student.query.get(int(sid))
    if not stu:
        return generate_res("failed")
    if request.method == "POST":
        stu.set_attrs(data)
        stu.auto_commit()
    return generate_res("success", data=stu.detail)
