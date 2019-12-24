from flask import jsonify
from flask import request

from .blueprint import api
from ..models import Student, Class, Department, level_models


def generate_res(status, data=None):
    return jsonify({
        "status": status,
        "data": data
    })


# 获取所有学院,班级信息
@api.route("/departments/")
def departments():
    data = {}
    dps = Department.query.all()
    data['departments'] = [{"id": dp.id, "name": dp.name} for dp in dps]
    data['classes'] = {dp.id: [{"id": c.id, "name": c.name} for c in dp.classes] for dp in dps}
    return generate_res("success", data=data)


# 获取班级所有学生信息
@api.route('/classes/students/<int:cid>')
def students(cid):
    class_ = Class.query.get(int(cid or -1))
    if not class_:
        return generate_res("failed")
    data = [{'id': s.id, 'name': s.name} for s in class_.student]
    return generate_res("success", data=data)


# 录入
@api.route('/record', methods=["POST"])
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


# 获取/修改学生信息
@api.route('/students/<int:sid>', methods=['POST', "GET"])
def change_info(sid):
    data = request.get_json()
    stu = Student.query.get(int(sid))
    if not stu:
        return generate_res("failed")
    if request.method == "POST":
        sex = data.get('sex')
        if sex not in ['男', '女']:
            return generate_res("failed")
        stu.set_attrs(data)
    return generate_res("success", data=stu.detail)


# 获取punish_levels, reward_levels,change_levels
@api.route('/changes/')
def changes():
    data = {name: model.all() for name, model in level_models.items()}
    return generate_res("success", data=data)
