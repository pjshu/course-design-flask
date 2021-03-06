import random

departments = [
    '资源环境与安全工程学院',
    '土木工程学院',
    '机电工程学院',
    '信息与电气工程学院',
    '计算机科学与工程学院',
    '化学化工学院',
    '数学与计算科学学院',
    '物理与电子科学学院',
    '生命科学学院',
    '建筑与艺术设计学院',
    '人文学院',
    '外国语学院',
    '马克思主义学院',
    '教育学院',
    '商学院',
    '艺术学院',
    '体育学院',
    '法学与公共管理学院',
    '材料科学与工程学院'
]

rewards = [
    '校特等奖学金',
    '校一等奖学金',
    '校二等奖学金',
    '校三等奖学金',
    '系一等奖学金',
    '系二等奖学金',
    '系三等奖学金'
]

change = ["转系", "休学", "复学", "退学"]

publishes = ["无", "警告", "严重", "警告", "记过", "记大过"]

numbers = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七"}


def generate_departments():
    return [{"name": department, "class_count": random.randint(1, 7)} for department in departments]
