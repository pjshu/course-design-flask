import random
import time

import pytest
from faker import Faker
from flask import url_for

fake = Faker('zh_CN')

student = None


def test_departments(client):
    res = client.get(url_for('api.departments'))
    data = res.get_json().get('data')
    assert len(data['classes']) != 0
    assert len(data['departments']) != 0


# 测试学生录入
@pytest.mark.repeat(10)
def test_record(client):
    res = client.post(url_for('api.record'), json={
        "class_id": 1,
        "name": fake.name(),
        "sex": random.choice(["男", "女"]),
        "birthday": int(time.time()),
        "native_place": fake.address()
    })
    assert b'success' in res.data


# 测试获取班级所有学生
def test_classes(client):
    res = client.get(url_for('api.classes', cid=1))
    data = res.get_json().get('data')
    global student
    student = [s['id'] for s in data]
    assert len(student) != 0


# 修改学生信息
def test_student_info(client):
    student_id = random.choice(student)
    res = client.post(url_for('api.student', sid=student_id), json={
        "class_id": 2,
        "name": fake.name(),
        "sex": random.choice(["男", "女"]),
        "birthday": int(time.time()),
        "native_place": fake.address(),
        "punish": {
            "level_id": 1,
            "description": "test"
        },
        "reward": {
            "level_id": 1,
            "description": "test"
        },
        "change": {
            "level_id": 1,
            "description": "test"
        }
    })
    assert b'success' in res.data


def test_changes(client):
    res = client.get(url_for('api.changes'))
    data = res.get_json()
    assert b'success' in res.data
    assert len(data.get('data')) != 0
