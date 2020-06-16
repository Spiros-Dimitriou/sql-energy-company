from random import randint

import pymysql

conn = pymysql.connect(host='150.140.186.217', port=3306, user='db19_up1046888', passwd='up1046888',
                       db='project_up1046888')
# conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='test')
cursor = conn.cursor()
sql = "SELECT ssn, address FROM Customer"
cursor.execute(sql)
result = cursor.fetchall()
# for i in result:
#     print i[0]
# print result
sql = "INSERT INTO Consumption_Meter VALUES (%s, %s, %s, %s, %s)"
for i in range(len(result)):
    cursor = conn.cursor()
    values = (i, result[i][0], result[i][1], randint(0, 15)/14, randint(1, 4))
    cursor.execute(sql, values)
conn.commit()
conn.close()
