from .blueprint import api
from .utils import generate_res
from ..models import Department


# 获取所有学院,班级信息
@api.route("/departments/")
def departments():
    data = {}
    dps = Department.query.all()
    data['departments'] = [{"id": dp.id, "name": dp.name} for dp in dps]
    data['classes'] = {dp.id: [{"id": c.id, "name": c.name} for c in dp.classes] for dp in dps}
    return generate_res("success", data=data)
