# 初始化数据库脚本
from .constant import change, rewards, publishes, generate_departments, numbers
from .models import Change_code, Reward_levels, Publish_levels, Department, Class


def commit_level(data, Model):
    count = 0
    for d in data:
        if not Model.query.filter_by(description=d).first():
            d = Model(count, d)
            d.auto_commit()
            count += 1


def init():
    commit_level(change, Change_code)
    commit_level(rewards, Reward_levels)
    commit_level(publishes, Publish_levels)

    departments: dict = generate_departments()
    for department in departments:
        d = Department(name=department['name'])
        classes = [Class(name=f"{department['name']}{numbers[n]}班") for n in range(1, department['class_count'] + 1)]
        d.classes.extend(classes)
        d.auto_commit()
