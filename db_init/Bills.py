from random import randint

import pymysql


conn = pymysql.connect(host='150.140.186.217', port=3306, user='db19_up1046888', passwd='up1046888',
                       db='project_up1046888')

cursor = conn.cursor()

query = "SELECT ssn FROM Customer"
cursor.execute(query)
customers = cursor.fetchall()

query = "INSERT INTO Bill VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)"
for i in customers:
    for j in range(5):
        date = '2019-' + str(7 + j) + '-1'

        # The reason that the 'bill temporary queries' are not the values of the tuple "values" ln 54 and are instead
        # individually executed is that if placed in the said tuple, they will be executed in the ln 57 and return a
        # tuple, which will cause an error in the final sql insert query
        bill_temp_query = """(SELECT MIN((CASE WHEN M2.Pmeter_ID IS NOT NULL THEN (M1.kWh-M2.kWh)*0.165 ELSE M1.kWh*0.165 END)) FROM Measurement AS M1, Measurement AS M2 WHERE M1.Date='""" + date + """' AND (CASE WHEN M2.Type=1 AND M2.Date='""" + date + """' THEN M2.Pmeter_ID=(SELECT Production_meter.Meter_ID FROM Production_meter WHERE Production_meter.Producer_Ssn='""" + i[0] + """"') ELSE M2.Pmeter_ID IS NULL END) AND M1.Cmeter_ID=(SELECT Consumption_meter.Meter_ID FROM Consumption_meter WHERE Consumption_meter.Consumer_Ssn='""" + i[0] + """'))"""
        cursor.execute(bill_temp_query)
        initial_amount = cursor.fetchone()[0]

        bill_temp_query = """(SELECT MIN((CASE WHEN M2.Pmeter_ID IS NOT NULL THEN (M1.kWh-M2.kWh)*0.165*(1-Contract.Discount_pct/100) ELSE M1.kWh*0.165*(1-Contract.Discount_pct/100) END)) FROM Measurement AS M1, Measurement AS M2, Contract WHERE M1.Date='""" + date + """' AND (CASE WHEN M2.Type=1 AND M2.Date='""" + date + """' THEN M2.Pmeter_ID=(SELECT Production_meter.Meter_ID FROM Production_meter WHERE Production_meter.Producer_Ssn='""" + i[0] + """') ELSE M2.Pmeter_ID IS NULL END) AND M1.Cmeter_ID=(SELECT Consumption_meter.Meter_ID FROM Consumption_meter WHERE Consumption_meter.Consumer_Ssn='""" + i[0] + """') AND Contract.Ssn='""" + i[0] + """')"""
        cursor.execute(bill_temp_query)
        final_amount = cursor.fetchone()[0]

        bill_temp_query = """(SELECT Contract.ID FROM Contract WHERE Contract.Ssn = """ + i[0] + """)"""
        cursor.execute(bill_temp_query)
        contract_id = cursor.fetchone()[0]

        bill_temp_query = """(SELECT Consumption_meter.Store_ID FROM Consumption_meter WHERE Consumption_meter.Consumer_Ssn = """ + i[0] + """)"""
        cursor.execute(bill_temp_query)
        store_id = cursor.fetchone()[0]

        bill_temp_query = """(SELECT Measurement.ID FROM Measurement, Production_meter WHERE Production_meter.Producer_Ssn = """ + i[0] + """ AND Production_meter.Meter_ID = Measurement.Pmeter_ID AND Measurement.Date = '""" + date + """')"""
        cursor.execute(bill_temp_query)
        p_measurement_id = cursor.fetchall()
        if p_measurement_id:
            p_measurement_id = p_measurement_id[0][0]
        else:
            p_measurement_id = None

        bill_temp_query = """(SELECT Measurement.ID FROM Measurement, Consumption_meter WHERE Consumption_meter.Consumer_Ssn = """ + i[0] + """ AND Consumption_meter.Meter_ID = Measurement.Cmeter_ID AND Measurement.Date = '""" + date + """')"""
        cursor.execute(bill_temp_query)
        c_measurement_id = cursor.fetchone()[0]

        values = (date, initial_amount, final_amount, i[0], contract_id, store_id, p_measurement_id, c_measurement_id)
        print values

        cursor.execute(query, values)
conn.commit()
conn.close()
