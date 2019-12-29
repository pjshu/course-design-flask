安装模块
```shell script
pip3 install -r requirements.txt --user
```


初始化数据库
```shell script
flask shell 
>>> create()  #创建表
>>> init()   # 初始化数据库
>>> drop() # 删除所有表
```

**覆盖率测试**
```shell script
py.test --cov=course_design test/ --repeat-scope=session -s
```

**测试100次**
```shell script
py.test --count=100 -x  -s
```

docker 构建
```shell script
docker build -t course-design ./ 
```

docker 运行
```shell script
docker run -d -p 8000:80 course-design
```


