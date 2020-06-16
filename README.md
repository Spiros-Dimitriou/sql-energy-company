# sql-energy-company
SQL database control for a company managing energy consumers and producers

This project is a collaboration with Konstantinos Sekaras. We both worked many hours for this.

SQL managing application using pymysql for a company that stores customer details, bills, information about measurements and contracts signed with the customers.
The safety of the data is not taken into account here, only the careful modeling of the db and some basic interface.
The Entity-Relationship diagram is in Greek, I'll update it when I get some time. The Relation diagram although is more than enough to understand the modeling.

Each customer is a consumer and can be a producer as well.
Every month, a consumption measurement is inserted and if they are a producer, then a production measurement as well.
Automatically, a bill is generated based on the amount of energy consumed and produced and the percentage of discount they get based on their characteristics (like having disability or multiple children).
The bill is inserted into the database and is visible through a number of ways.

The app lets you either search, edit, insert and delete some particular data on the
database. Briefly explained below:

1) Search for a customer's:
	1a) Bills
		1ai) All bills
		1aii) A single bill
	1b) Measurements
		1bi) All measurements
		1bii) Only production/only consumption measurements
		1biii) A single measurement
	1c) Contract
		1ci) The contract signed with the company

2) Edit a customer's:
	2a) Measurements
		2ai) Insert/Overwrite measurement
	2b) Bills
		2bi) Delete a bill
		2bii) Create a bill
    
