README file for EnergySystem db initialization codes

Table creation.sql contains the sql code to create the db tables

Codes for inserting
	Customers
	Consumers
	Producers
	Contracts
	Regional Stores
are in sql and were done manually. Codes for inserting
	Consumption meters
	Production meters
	Measurements
	Bills
are in python using pymysql, are more repetitive, and were based on
the first set of data.

Relation Diagram contains information about which data needs to be
inserted ahead of others.
Recommended way:
1) Regional Store
2) Customer
3) Contract
4) Consumer
5) Producer (if exists)
6) Consumption meter
7) Production meter (if exists)
8) Measurements
9) Bills
