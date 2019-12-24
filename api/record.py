from flask import jsonify
from flask import request

from .blueprint import api
from ..models import Student, Class, models, organizations, level_models


def generate_res(status, data=None):
    return jsonify({
        "status": status,
        "data": data
    })


# 获取所有学院信息,一个学院所有班级信息,一个班级所有学生信息
@api.route("/organization/<string:type_>/", methods=["POST", "GET"])
def organization(type_):
    data = request.get_json() or {}
    org_members = organizations[type_](data.get('org_id'))
    data = []
    if not org_members:
        return generate_res("failed")
    for members in org_members:
        data.append({
            'id': members.id,
            'name': members.name
        })
    return generate_res("success", data)


# 按班级录入, 获取班级单个学生信息
@api.route('/students/<int:sid>')
@api.route('/students/', methods=['POST'], defaults={'sid': ''})
def record(sid):
    data = request.get_json()
    if request.method == 'POST':
        class_id = data.get('class_id')
        student_id = data.get('student_id')
        class_ = Class.query.get(int(class_id))
        sex = data.get('sex')
        if not class_ and sex not in ['男', '女']:
            return generate_res("failed")
        student = Student.query.get(int(student_id or -1)) or Student()
        student.set_attrs(data)
        # 修改班级时先删除班级学生
        class_.add_student(student)
        class_.auto_commit()
        return generate_res("success")
    stu = Student.query.get(int(sid))
    return generate_res("success", data=stu.detail)


# 获取/修改 学生惩罚,奖励,学籍变更情况
@api.route('/students/state/<string:type_>', methods=["POST"])
@api.route('/students/state', defaults={"type_": ''})
def change_state(type_):
    Model = models[type_]
    data = request.get_json()
    student_id = data.get('student_id')
    model = Model.query.filter_by(student_id=int(student_id)).first() or Model()
    if request.method == "POST":
        # levels ,description,student_id
        state = "success"
        try:
            model.set_attrs(data)
            model.auto_commit()
        except:
            state = "failed"
        return generate_res(state)
    data = {}
    try:
        data["description"] = model.change_description
    except:
        return generate_res("failed")
    return generate_res("success", data=data)


@api.route('/changes/<string:type_>/')
def changes(type_):
    levels = level_models[type_].all()
    data = []
    for level in levels:
        data.append({"code": level.code, "description": level.description})
    return generate_res("success", data=data)
