from django.db import connection

def execute_sql(sql):
    cursor = connection.cursor()
    print(sql)
    cursor.execute(sql)
