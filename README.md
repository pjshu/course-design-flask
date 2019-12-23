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

