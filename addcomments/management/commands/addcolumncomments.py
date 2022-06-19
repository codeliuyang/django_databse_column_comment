""" ADD COMMENT TO TABLE COLUMNS
only support MySQL for now

command 'python manage.py addcolumncomments'

ALTER TABLE supplier_seller COMMENT '联营商';

ALTER TABLE children
MODIFY COLUMN school varchar(100) DEFAULT NULL COMMENT '学校'

"""
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections
from django.apps import apps


class Command(BaseCommand):
    help = 'alter table columns to add comment with the verbose_name of model'

    def add_arguments(self, parser):
        # 增加数据库配置
        parser.add_argument(
            '--database',
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to synchronize. Defaults to the "default" database.',
        )

    def handle(self, *args, **options):
        # 1. 第一步连接数据库
        database = options['database']
        connection = connections[database]
        connection.prepare_database()
        cursor = connection.cursor()
        # 2. 找出所有自己定义的models
        models = apps.get_models()
        custom_models = [model for model in models if 'django.contrib' not in str(model)]
        for modelobj in custom_models:
            # 2.1 获取table_name
            table_name = modelobj._meta.db_table
            # 2.2 从数据库中获取 ddl of create table ...
            ddl_sql = "show create table " + table_name
            cursor.execute(ddl_sql)
            ddl_result = cursor.fetchall()
            table_ddl = ddl_result[0][1]
            ddl_texts = table_ddl.split("\n")
            ddl_column_dict = {}
            for ddl_text in ddl_texts:
                ddl_text = ddl_text.strip()
                # 找到属于字段的行
                if ddl_text[0] == '`':
                    next_index = ddl_text.index("`", 1, len(ddl_text))
                    column_key = ddl_text[1: next_index]
                    if column_key == 'id':
                        continue
                        # 移除comment
                    comment_index = ddl_text.find("COMMENT")
                    ddl_column_dict[column_key] = ddl_text[0:comment_index]
            # 3. 遍历model的字段
            fields = modelobj._meta.fields
            for field in fields:
                db_column = field.db_column
                if not db_column:
                    db_column = field.name
                # 3.1 set verbose_name as comment
                verbose_name = field.verbose_name
                if not verbose_name or verbose_name == db_column.replace("_", " "):
                    continue
                model_comment_sql = "-- FOR " + table_name + "." + db_column + " \n"
                model_comment_sql += "\t" + "ALTER TABLE " + table_name + "\n"
                model_comment_sql += "\t" + "MODIFY COLUMN "
                field_type = str(type(field))
                if "AutoField" in str(field_type) or "Foreign" in str(field_type):
                    continue
                original_ddl = ddl_column_dict.get(db_column)
                model_comment_sql += original_ddl + " COMMENT '" + str(verbose_name) + "'"
                self.stdout.write(model_comment_sql)
                cursor.execute(model_comment_sql)
                connection.commit()
        connection.close()
