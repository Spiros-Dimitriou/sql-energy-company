import pymysql

# Database credentials
host_ip = ''
port = ''
username = ''
password = ''
db_name = ''

yes = {'yes', 'y', 'ye', ''}
no = {'no', 'n'}

conn = pymysql.connect(host=host_ip, port=port, user=username, passwd=password, db=db_name)


# Checks if the ssn refers to a customer
def is_customer(ssn):
    cursor = conn.cursor()
    query = "SELECT * FROM Customer WHERE Ssn = %s"
    cursor.execute(query, ssn)
    if cursor.fetchone():
        # Is a customer
        return 1
    else:
        # Isn't a customer
        return 0


# Displays details about the contract of a customer
def view_contract(ssn):
    cursor = conn.cursor()
    query = "SELECT * FROM Contract WHERE Contract.Ssn = %s"
    cursor.execute(query, ssn)
    contract = cursor.fetchone()
    query = "SELECT Name, Disability, Multichild, Salary FROM Customer WHERE Customer.Ssn = %s"
    cursor.execute(query, ssn)
    identity = cursor.fetchone()
    print(
        "\nContract regarding mr/mrs {}\nService type: {}\nDiscount percentage: {}%\nBased on:\n  Multiple children: {}\n  Disabled: {}\n  Salary: {}\nContract signed on: {}".format(
            identity[0], 'Home' if (contract[2] == 0) else 'Business', contract[1], 'yes' if identity[2] == 1 else 'no',
            'yes' if identity[1] == 1 else 'no',
            identity[3], str(contract[4])[:-9]))


# Checks if the ssn refers to a producer
def is_producer(ssn):
    query = "SELECT * FROM Producer WHERE Producer.Ssn = %s"
    cursor = conn.cursor()
    cursor.execute(query, ssn)
    result = cursor.fetchone()
    if result:
        # Is a producer
        return 1
    else:
        # Isn't a producer
        return 0


# Inserts a bill into the database provided that the measurements have already been inserted
def create_bill(ssn, date):
    cursor = conn.cursor()

    # Gather information for bill creation
    bill_temp_query = """(SELECT MIN((CASE WHEN M2.Pmeter_ID IS NOT NULL THEN (M1.kWh-M2.kWh)*0.165 ELSE M1.kWh*0.165 END)) FROM Measurement AS M1, Measurement AS M2 WHERE M1.Date='""" + date + """' AND (CASE WHEN M2.Type=1 AND M2.Date='""" + date + """' THEN M2.Pmeter_ID=(SELECT Production_meter.Meter_ID FROM Production_meter WHERE Production_meter.Producer_Ssn='""" + ssn + """"') ELSE M2.Pmeter_ID IS NULL END) AND M1.Cmeter_ID=(SELECT Consumption_meter.Meter_ID FROM Consumption_meter WHERE Consumption_meter.Consumer_Ssn='""" + ssn + """'))"""
    cursor.execute(bill_temp_query)
    initial_amount = cursor.fetchone()[0]
    if not initial_amount:
        # There is no measurement corresponding to the requested bill and the bill cannot be created
        print ("Insufficient information for bill extraction")
        return

    bill_temp_query = """(SELECT Measurement.ID FROM Measurement, Production_meter WHERE Production_meter.Producer_Ssn = %s AND Production_meter.Meter_ID = Measurement.Pmeter_ID AND Measurement.Date = %s)"""
    cursor.execute(bill_temp_query, (ssn, date))
    p_measurement_id = cursor.fetchall()
    if p_measurement_id:
        p_measurement_id = p_measurement_id[0][0]
    else:
        p_measurement_id = None

    if is_producer(ssn) and not p_measurement_id:
        # Checking if the customer is a producer, and if they are and a production measurement is not inserted,
        # the bill cannot be created
        print ("Production measurement not inserted")
        return

    bill_temp_query = """(SELECT MIN((CASE WHEN M2.Pmeter_ID IS NOT NULL THEN (M1.kWh-M2.kWh)*0.165*(1-Contract.Discount_pct/100) ELSE M1.kWh*0.165*(1-Contract.Discount_pct/100) END)) FROM Measurement AS M1, Measurement AS M2, Contract WHERE M1.Date='""" + date + """' AND (CASE WHEN M2.Type=1 AND M2.Date='""" + date + """' THEN M2.Pmeter_ID=(SELECT Production_meter.Meter_ID FROM Production_meter WHERE Production_meter.Producer_Ssn='""" + ssn + """') ELSE M2.Pmeter_ID IS NULL END) AND M1.Cmeter_ID=(SELECT Consumption_meter.Meter_ID FROM Consumption_meter WHERE Consumption_meter.Consumer_Ssn='""" + ssn + """') AND Contract.Ssn='""" + ssn + """')"""
    cursor.execute(bill_temp_query)
    final_amount = cursor.fetchone()[0]

    bill_temp_query = """(SELECT Contract.ID FROM Contract WHERE Contract.Ssn = %s)"""
    cursor.execute(bill_temp_query, ssn)
    contract_id = cursor.fetchone()[0]

    bill_temp_query = """(SELECT Consumption_meter.Store_ID FROM Consumption_meter WHERE Consumption_meter.Consumer_Ssn = %s)"""
    cursor.execute(bill_temp_query, ssn)
    store_id = cursor.fetchone()[0]

    bill_temp_query = """(SELECT Measurement.ID FROM Measurement, Consumption_meter WHERE Consumption_meter.Consumer_Ssn = %s AND Consumption_meter.Meter_ID = Measurement.Cmeter_ID AND Measurement.Date = %s)"""
    cursor.execute(bill_temp_query, (ssn, date))
    c_measurement_id = cursor.fetchone()[0]
    values = (date, initial_amount, final_amount, ssn, contract_id, store_id, p_measurement_id, c_measurement_id)

    query = "INSERT INTO Bill VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, values)
    if raw_input("Display bill? (Y/N)") in no:
        return
    view_bill(ssn, date)


# Inserts a measurement into the database
def insert_measurement(ssn, date, kwh, prodcons):
    # prodcons = 1 for production measurement
    # prodcons = 0 for consumption measurement

    # Find the meter id for the consumption meter or production meter

    if prodcons:
        query = "SELECT * FROM Production_meter WHERE Producer_Ssn = %s"
    else:
        query = "SELECT * FROM Consumption_meter WHERE Consumer_Ssn = %s"
    cursor = conn.cursor()
    cursor.execute(query, ssn)
    meter_id = cursor.fetchone()[0]
    # Determine if the measurement to be inserted refers to same date as an existing measurement
    if prodcons:
        query = "SELECT * FROM Measurement WHERE Measurement.Date = %s AND Measurement.Pmeter_ID = %s"
    else:
        query = "SELECT * FROM Measurement WHERE Measurement.Date = %s AND Measurement.Cmeter_ID = %s"
    cursor.execute(query, (date, meter_id))
    measurement = cursor.fetchall()

    if measurement:
        if raw_input(
                "A measurement of that date has already been inserted.\n If overwritten, the associated bill will be deleted as well.\n Overwrite? (Y/N)").lower() in no:
            return
        else:
            # Delete associated bill
            query = "DELETE FROM Bill WHERE Bill.Ssn = %s AND Bill.Month_of_Measurement = %s"
            cursor.execute(query, (ssn, date))
            # Delete previous measurement
            query = "DELETE FROM `Measurement` WHERE `Measurement`.`ID` = %s"
            cursor.execute(query, measurement[0][0])
            print("Bill deleted")

    # Insertion of the measurement
    if prodcons:
        query = "INSERT INTO `Measurement` (`ID`, `Type`, `kWh`, `Date`, `Pmeter_ID`, `Cmeter_ID`) VALUES (NULL, 1, %s, %s, %s, NULL)"
    else:
        query = "INSERT INTO `Measurement` (`ID`, `Type`, `kWh`, `Date`, `Pmeter_ID`, `Cmeter_ID`) VALUES (NULL, 0, %s, %s, NULL, %s)"
    cursor.execute(query, (kwh, date, meter_id))
    print ("Measurement inserted")


# Displays details about a particular bill for a customer
def view_bill(ssn, date):
    # Determine extra information to be included in the bill
    query = "SELECT * FROM Bill WHERE Bill.Ssn = %s AND Bill.Month_of_Measurement = %s"
    cursor = conn.cursor()
    cursor.execute(query, (ssn, date))
    bill = cursor.fetchone()
    if not bill:
        print ("\nThe requested bill doesn't exist. Insert the corresponding measurement(s) in order to create it")
        return

    # Customer name and address
    query = "SELECT Name, Address FROM Customer WHERE Customer.Ssn = %s"
    cursor.execute(query, ssn)
    identity = cursor.fetchone()

    # Service type and discount
    query = "SELECT Discount_pct, Invoice_type FROM Contract WHERE Contract.ID = %s"
    cursor.execute(query, bill[5])
    contract = cursor.fetchone()

    # Store address
    query = "SELECT Address FROM Regional_store WHERE Regional_store.ID = %s"
    cursor.execute(query, bill[6])
    store_address = cursor.fetchone()[0]

    # Print out bill if it exists
    if bill:
        print (
            "\nBill no. {} \nYear/Month: {}\nCustomer name: {} \nCustomer SSN: {}\nAddress: {} \nService Type: {}\nAmount: ${}\nAmount to be paid based on discount: ${}\nDiscount percentage: {}%\nYour store: {}".format(
                bill[0], str(date)[:-3], identity[0], bill[4], identity[1],
                'Home' if (contract[1] == 0) else 'Business', round(bill[2], 2), round(bill[3], 2), contract[0], store_address))
    else:
        print ("The bill requested does not exist")


# Deletes bill from database with same inputs as view_bill
def delete_bill(ssn, date):
    query = "DELETE FROM Bill WHERE Bill.Ssn = %s AND Bill.Month_of_Measurement = %s"
    cursor = conn.cursor()
    cursor.execute(query, (ssn, date))
    print ("Bill deleted")


# Displays all bills of a customer (uses view_bill function)
def view_all_bills(ssn):
    cursor = conn.cursor()
    query = "SELECT Month_of_Measurement FROM Bill WHERE Ssn = %s"
    cursor.execute(query, ssn)
    dates = cursor.fetchall()
    if dates:
        pass
    else:
        print ("There are no bills for that customer")
        return
    for date in dates:
        view_bill(ssn, date[0])
        print ("\n")


# Displays details about a measurement
def view_measurement(ssn, date, prodcons):
    cursor = conn.cursor()
    # 1 for production measurement
    # 0 for consumption measurement
    meter_id = find_meter_id(ssn, prodcons)
    if prodcons:
        # Production measurement
        query = "SELECT * FROM Measurement WHERE Pmeter_ID = %s AND Date = %s"
        cursor.execute(query, (meter_id, date))
        measurement = cursor.fetchone()
        if measurement:
            pass
        else:
            return -1

    else:
        # Consumption measurement
        query = "SELECT * FROM Measurement WHERE Cmeter_ID = %s AND Date = %s"
        cursor.execute(query, (meter_id, date))
        measurement = cursor.fetchone()
        if measurement:
            pass
        else:
            return -1

    print ("\nMeasurement ID: {}\nMeter ID: {}\nDate: {}\nKWh: {} {}".format(measurement[0], meter_id, str(date)[:-3],
                                                                           measurement[2],
                                                                           'Produced' if prodcons else 'Consumed'))


# Returns the meter identification provided the type of the meter for a customer
def find_meter_id(ssn, prodcons):
    cursor = conn.cursor()
    if prodcons:
        # Production meter ID
        query = "SELECT Meter_ID FROM Production_meter WHERE Producer_Ssn = %s"
        cursor.execute(query, ssn)
        return cursor.fetchone()[0]
    else:
        # Consumption meter ID
        query = "SELECT Meter_ID FROM Consumption_meter WHERE Consumer_Ssn = %s"
        cursor.execute(query, ssn)
        return cursor.fetchone()[0]


# Displays all measurements, type depending on allprodcons
def view_all_measurements(ssn, allprodcons):
    cursor = conn.cursor()
    meter_id = find_meter_id(ssn, 0)
    # All measurements : 2
    # Only production measurements: 1
    # Only consumption measurements: 0
    if allprodcons == 0 or allprodcons == 2:
        query = "SELECT Date from Measurement WHERE Cmeter_ID = %s"
        cursor.execute(query, meter_id)
        dates = cursor.fetchall()
        for date in dates:
            view_measurement(ssn, date[0], 0)
            print ("\n")

    if (allprodcons == 1 or allprodcons == 2) and is_producer(ssn):
        query = "SELECT Date from Measurement WHERE Pmeter_ID = %s"
        cursor.execute(query, meter_id)
        dates = cursor.fetchall()
        for date in dates:
            view_measurement(ssn, date[0], 1)
            print ("\n")


# Returns an ssn entered by the user after making sure it is of correct length and exists in db
def input_ssn():
    ssn = int(input("Enter customer's ssn:\n"))
    ssn = str(ssn)
    if len(ssn) != 6:
        raise ValueError("Ssn has incorrect length. Must be 6 digits")
    if is_customer(ssn):
        return ssn
    else:
        raise ValueError("Customer not in database")


# Returns KWh entered by user after checks
def input_kwh():
    kwh = float(input("Enter kwh:\n"))
    if kwh < 0:
        raise ValueError("Kwh must be a positive number")
    return kwh


# Returns formatted year-month entered by user
def input_year_month():
    year = int(input("Enter year:\n"))
    year = str(year)
    if len(year) != 4:
        raise ValueError("Incorrect year input")
    month = int(input("Enter month:\n"))
    if month > 12 or len(str(month)) > 2:
        raise ValueError("Incorrect month input")
    month = str(month)
    if len(month) == 1:
        return year + '-0' + month + '-01'
    else:
        return year + '-' + month + '-01'


# Interfaces the ui with backend for view_all_bills
def display_all_bills_ui():
    view_all_bills(input_ssn())


# Interfaces the ui with backend for view_bill
def display_single_bill_ui():
    ssn = input_ssn()
    date = input_year_month()
    view_bill(ssn, date)


# Interfaces the ui with backend for view_all_measurements
def display_all_measurements_ui(allprodcons):
    ssn = input_ssn()
    if not (is_producer(ssn)) and allprodcons == 1:
        raise ValueError("Customer is not a producer")
    view_all_measurements(ssn, allprodcons)


# Interfaces the ui with backend for view measurement
def display_single_measurement_ui(prodcons):
    ssn = input_ssn()
    if not (is_producer(ssn)) and prodcons:
        raise ValueError("Customer is not a producer")
    date = input_year_month()
    if view_measurement(ssn, date, prodcons) == -1:
        print("No such measurement found\n")


# Interfaces the ui with backend for view_contract
def display_contract_ui():
    view_contract(input_ssn())


def insert_replace_measurement_ui(prodcons):
    ssn = input_ssn()
    if not (is_producer(ssn)) and prodcons:
        raise ValueError("Customer is not a producer")
    date = input_year_month()
    kwh = input_kwh()
    insert_measurement(ssn, date, kwh, prodcons)


def create_bill_ui():
    ssn = input_ssn()
    date = input_year_month()
    create_bill(ssn, date)


def delete_bill_ui():
    ssn = input_ssn()
    date = input_year_month()
    delete_bill(ssn, date)


print ("Welcome to ENergy inc. DAtabase MAnipulator ENDAMA(R)")
while True:
    try:
        user_choice = int(input(
            "\n\nInsert preference:\n1. Search info\n2. Edit info\n0. Exit\n"))

        # Choose what type of info to search for
        if user_choice == 1:
            user_choice = int(input(
                "1. View customer bills\n2. View customer measurements\n3. View customer contract\n0. Exit\n"))

            # Choose a way to display bills
            if user_choice == 1:
                user_choice = int(input("1. All bills\n2. Single bill\n0. Exit\n"))

                # All bills
                if user_choice == 1:
                    display_all_bills_ui()

                # Single bill
                if user_choice == 2:
                    display_single_bill_ui()

            # Choose a way to display measurements
            elif user_choice == 2:
                user_choice = int(input(
                    "1. All measurements\n2. All consumption measurements\n3. All production measurements\n4. Single consumption measurement\n5. Single production measurement\n0. Exit\n"))

                # All measurements
                if user_choice == 1:
                    display_all_measurements_ui(2)

                # All consumption measurements
                elif user_choice == 2:
                    display_all_measurements_ui(0)

                # All production measurements
                elif user_choice == 3:
                    display_all_measurements_ui(1)

                # Single consumption measurement
                elif user_choice == 4:
                    display_single_measurement_ui(0)

                # Single production measurement
                elif user_choice == 5:
                    display_single_measurement_ui(1)

            elif user_choice == 3:
                # View customer contract
                display_contract_ui()

        elif user_choice == 2:
            # Edit info in database
            user_choice = int(input(
                "1. Insert/replace consumption measurement\n2. Insert/replace production measurement\n3. Create bill\n4. Delete bill\n0. Exit\n"))

            # Insert/replace consumption measurement
            if user_choice == 1:
                insert_replace_measurement_ui(0)

            # Insert/replace consumption measurement
            elif user_choice == 2:
                insert_replace_measurement_ui(1)

            # Create bill
            elif user_choice == 3:
                create_bill_ui()

            # Delete bill
            elif user_choice == 4:
                delete_bill_ui()

        # Exit app
        elif user_choice == 0:
            print ("Program exit")
            break

    except NameError:
        print ("Invalid input")
    except ValueError as v:
        print (v)
    except SyntaxError:
        print ("Invalid input")
    except TypeError:
        print ("Invalid input")

conn.commit()
conn.close()
