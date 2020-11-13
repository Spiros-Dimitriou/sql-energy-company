from random import randint

import pymysql

# conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='test')
cursor = conn.cursor()
sql = "SELECT ssn FROM Customer WHERE ssn IN (SELECT ssn FROM Producer)"
cursor.execute(sql)
result = cursor.fetchall()
sql = "INSERT INTO Production_meter VALUES (%s, %s)"
for i in range(len(result)):
    cursor = conn.cursor()
    values = (i, result[i][0])
    cursor.execute(sql, values)
conn.commit()
conn.close()
