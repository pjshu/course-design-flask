import random
import time

import pytest
from faker import Faker
from flask import url_for

fake = Faker('zh_CN')

student = None


# 测试学生录入
@pytest.mark.repeat(4)
def test_record(client):
    res = client.post(url_for('api.record'), json={
        "class_id": 1,
        "name": fake.name(),
        "sex": random.choice(["男", "女"]),
        "birthday": int(time.time()),
        "native_place": fake.address()
    })
    assert b'success' in res.data


# 测试获取所有学院信息
def test_organization_department(client):
    res = client.get(url_for('api.organization', type_='department'))
    assert b'success' in res.data


# 测试获取所有班级信息
def test_organization_classes(client):
    res = client.post(url_for('api.organization', type_='class'), json={
        "org_id": 1
    })
    assert b'success' in res.data
    assert len(res.get_json().get('data')) != 0


# 测试获取班级所有学生信息
def test_organization_student(client):
    res = client.post(url_for('api.organization', type_='student'), json={
        "org_id": 1
    })
    students = res.get_json().get('data')
    global student
    student = [s['id'] for s in students]
    assert b'success' in res.data
    assert len(students) != 0


# 测试修改学生班级
def test_change_student(client):
    res = client.post(url_for('api.record'), json={
        "student_id": random.choice(student),
        "class_id": 2,
        "name": fake.name(),
        "sex": random.choice(["男", "女"]),
        "birthday": int(time.time()),
        "native_place": fake.address()
    })
    assert b'success' in res.data


# 测试获取单个学生信息
def test_student(client):
    res = client.get(url_for('api.record', sid=random.choice(student)))
    assert b'success' in res.data
    assert len(res.get_json()) != 0


# 测试添加惩罚信息
def test_publish(client):
    res = client.post(url_for('api.change_state', type_='punish'), json={
        "student_id": random.choice(student),
        "levels": random.randint(0, 5),
        "description": "",
    })
    assert b'success' in res.data


# 测试添加奖励信息
def test_reward(client):
    res = client.post(url_for('api.change_state', type_='reward'), json={
        "student_id": random.choice(student),
        "levels": random.randint(0, 6),
        "description": ""
    })
    assert b'success' in res.data


# 测试添加学籍变动
def test_change(client):
    res = client.post(url_for('api.change_state', type_='change'), json={
        "student_id": random.choice(student),
        "levels": random.randint(0, 4),
        "description": ""
    })
    assert b'success' in res.data


def test_changes_punish(client):
    res = client.get(url_for('api.changes', type_='punish'))
    data = res.get_json()
    assert b'success' in res.data
    assert len(data.get('data')) != 0


def test_changes_reward(client):
    res = client.get(url_for('api.changes', type_='reward'))
    data = res.get_json()
    assert b'success' in res.data
    assert len(data.get('data')) != 0


def test_changes_change(client):
    res = client.get(url_for('api.changes', type_='change'))
    data = res.get_json()
    assert b'success' in res.data
    assert len(data.get('data')) != 0
