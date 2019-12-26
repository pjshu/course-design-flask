from .blueprint import api
from .utils import generate_res
from ..models import Class


# 获取班级所有学生信息
@api.route('/classes/<cid>/')
def classes(cid):
    class_ = Class.query.get(int(cid or -1))
    if not class_:
        return generate_res("failed")
    data = [{'id': s.id, 'name': s.name} for s in class_.student]
    return generate_res("success", data=data)
