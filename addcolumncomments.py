""" 给表和字段添加注释

暂时仅使用MySQL

ALTER TABLE supplier_seller COMMENT '联营商';

ALTER TABLE children
MODIFY COLUMN school varchar(100) DEFAULT NULL COMMENT '学校'

"""
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections
from django.apps import apps


class Command(BaseCommand):
    help = 'alter table columns to add comment for columns'

    def add_arguments(self, parser):
        # 增加数据库配置
        parser.add_argument(
            '--database',
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to synchronize. Defaults to the "default" database.',
        )
        # 增加app_label
        parser.add_argument(
            'app_label', nargs='?',
            help='App label of an application to synchronize the state.',
        )

    def handle(self, *args, **options):
        # 1. 第一步连接数据库
        database = options['database']
        connection = connections[database]
        connection.prepare_database()
        cursor = connection.cursor()

        # 2. 找出所有自己定义的models
        app_label = options['app_label']
        if app_label is None:
            print("please add param [app_label], such as [python manage.py addcolumncomments polls]")
            return None
        custom_models = apps.get_app_config(app_label).models
        for model_name in custom_models:

            modelobj = custom_models[model_name]

            # 如果自己定义了table_name，那就以定义的为准，否则就是默认的Django模型Model的类名为 应用名+下划线+模型类名
            table_name = modelobj._meta.db_table
            if not table_name:
                table_name = app_label + '_' + model_name

            # 遍历属性
            fields = modelobj._meta.fields
            for field in fields:
                model_comment_sql = "-- model_comment_sql for " + table_name + "\n"
                model_comment_sql += "ALTER TABLE " + table_name + "\n"

                db_column = field.db_column
                verbose_name = field.verbose_name

                if not verbose_name:
                    continue

                if not db_column:
                    db_column = field.name
                model_comment_sql += "MODIFY COLUMN " + db_column
                field_type = str(type(field))
                if "AutoField" in str(field_type):
                    continue
                model_comment_sql += " " + model_filed_type_to_sql_type(field_type, field.max_length)

                if field.null:
                    if field.default is None:
                        model_comment_sql += " " + "DEFAULT NULL"
                    elif "NOT_PROVIDED" in str(field.default):
                        model_comment_sql += " " + "DEFAULT NULL"
                    elif field.default is False:
                        model_comment_sql += ""
                    else:
                        model_comment_sql += " " + "DEFAULT '" + str(field.default) + "'"
                else:
                    model_comment_sql += " " + "NOT NULL"

                model_comment_sql += " " + "COMMENT '" + str(verbose_name) + "'"

                print(model_comment_sql)

                cursor.execute(model_comment_sql)
                connection.commit()


def model_filed_type_to_sql_type(field_type, max_length):
    if "DateTimeField" in field_type:
        return "datetime(6)"
    if "IntegerField" in field_type:
        return "int(11)"
    if "CharField" in field_type:
        return "varchar(" + str(max_length) + ")"
    if "FloatField" in field_type:
        return "double"
    if "BooleanField" in field_type:
        return "tinyint(1)"
