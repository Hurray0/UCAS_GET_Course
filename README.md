# UCAS GET Course
> 国科大抢课脚本

## 说明
**多线程暴力刷课**

尽量把注释写的很清楚了，**如果教务有大改动的话不负责更新**，有小bug请随时发issue

**需要填写的部分：**
```Python
username = ''  # 教务登录email
password = ''  # 教务登录password
course = [
        ('091M7010H', 0),
        ('091M7004H', 1),
    ]  # 需要抢课的课程号，格式('课程号', 学位课？)，1是学位课，0是非学位课
```

## 例图
![](/Users/hurray/$/spider/UCAS_GET_Course/img/Snip20170602_17.png)
![](/Users/hurray/$/spider/UCAS_GET_Course/img/Snip20170602_15.png)
![](/Users/hurray/$/spider/UCAS_GET_Course/img/Snip20170602_16.png)