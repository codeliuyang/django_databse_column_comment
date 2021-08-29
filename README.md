# django_mysql_comment
auto add comment for mysql table and column

## How to use

place the file ```addcolumncomments.py``` into the directory(`management/commands`) of one django app

such as ```polls/management/commands/addcolumncommnets.py```

next, run the command ```python manage.py addcolumncomments [appname]```

then, you will see the log in the console...
```
% python manage.py addcolumncomments polls

-- model_comment_sql for children.password
ALTER TABLE children
MODIFY COLUMN password varchar(300) DEFAULT NULL COMMENT '密码'

-- model_comment_sql for children.age
ALTER TABLE children
MODIFY COLUMN age int(11) NOT NULL COMMENT '年龄'
......
```

## If any bug
you can fix by yourself or commit your issue here, I will fix

## TODO

- how to use by ```pip install ...```
- use more django skills in the script
