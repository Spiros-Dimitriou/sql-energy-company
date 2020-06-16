from random import randint

import pymysql

conn = pymysql.connect(host='150.140.186.217', port=3306, user='db19_up1046888', passwd='up1046888',
                       db='project_up1046888')
# conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='test')
cursor = conn.cursor()
sql = "SELECT meter_id FROM Consumption_Meter"
cursor.execute(sql)
result = cursor.fetchall()
# for i in result:
#     print i[0]
# print result
sql = "INSERT INTO `Measurement` (`ID`, `Type`, `kWh`, `Date`, `Pmeter_ID`, `Cmeter_ID`) VALUES (NULL, 0, %s, %s, " \
      "NULL, %s)"
for i in result:
    for j in range(5):
        cursor = conn.cursor()
        values = (randint(500000, 1500000)/1000., '2019-'+str(7+j)+'-1', i[0])
        cursor.execute(sql, values)
conn.commit()
conn.close()
