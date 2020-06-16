CREATE TABLE `Customer` (
	`Ssn` varchar(255) NOT NULL,
	`Phone_Nunber` varchar(255) NOT NULL,
	`Disability` BOOLEAN NOT NULL,
	`Multichild` BOOLEAN NOT NULL,
	`Name` varchar(255) NOT NULL,
	`Address` varchar(255) NOT NULL,
	`Salary` INT(16) NOT NULL,
	PRIMARY KEY (`Ssn`)
);

CREATE TABLE `Consumer` (
	`Ssn` varchar(255) NOT NULL,
	`Consumer_ID` varchar(255) NOT NULL,
	PRIMARY KEY (`Ssn`)
);

CREATE TABLE `Producer` (
	`Ssn` varchar(255) NOT NULL,
	`Producer_ID` varchar(255) NOT NULL,
	PRIMARY KEY (`Ssn`)
);

CREATE TABLE `Production_meter` (
	`Meter_ID` varchar(255) NOT NULL,
	`Producer_Ssn` varchar(255) NOT NULL,
	PRIMARY KEY (`Meter_ID`)
);

CREATE TABLE `Consumption_Meter` (
	`Meter_ID` varchar(255) NOT NULL,
	`Consumer_Ssn` varchar(255) NOT NULL,
	`Address` varchar(255) NOT NULL,
	`Phases` BOOLEAN NOT NULL,
	`Store_ID` INT(10) NOT NULL,
	PRIMARY KEY (`Meter_ID`)
);

CREATE TABLE `Measurement` (
	`ID` INT(10) NOT NULL AUTO_INCREMENT,
	`Type` BOOLEAN NOT NULL,
	`kWh` FLOAT(16) NOT NULL,
	`Date` DATE NOT NULL,
	`Pmeter_ID` varchar(255) NOT NULL,
	`Cmeter_ID` varchar(255) NOT NULL,
	PRIMARY KEY (`ID`)
);

CREATE TABLE `Regional_store` (
	`ID` INT(10) NOT NULL,
	`Address` varchar(255) NOT NULL,
	PRIMARY KEY (`ID`)
);

CREATE TABLE `Bill` (
	`Bill_number` INT(30) NOT NULL AUTO_INCREMENT,
	`Month_of_Measurement` DATE NOT NULL,
	`Initial_Amount` FLOAT(32) NOT NULL,
	`Final_Amount` FLOAT(32) NOT NULL,
	`Ssn` varchar(255) NOT NULL,
	`Contract_ID` INT(30) NOT NULL,
	`Store_ID` INT(10) NOT NULL,
	`P_Measurement _ID` INT(10) NOT NULL,
	`C_Measurement _ID` INT(10) NOT NULL,
	PRIMARY KEY (`Bill_number`)
);

CREATE TABLE `Contract` (
	`ID` INT(30) NOT NULL AUTO_INCREMENT,
	`Discount_pct` FLOAT(10) NOT NULL,
	`Invoice_type` BOOLEAN NOT NULL,
	`Ssn` varchar(255) NOT NULL,
	`Signing_date` DATETIME NOT NULL,
	PRIMARY KEY (`ID`)
);

ALTER TABLE `Consumer` ADD CONSTRAINT `Consumer_fk0` FOREIGN KEY (`Ssn`) REFERENCES `Customer`(`Ssn`);

ALTER TABLE `Producer` ADD CONSTRAINT `Producer_fk0` FOREIGN KEY (`Ssn`) REFERENCES `Customer`(`Ssn`);

ALTER TABLE `Production_meter` ADD CONSTRAINT `Production_meter_fk0` FOREIGN KEY (`Producer_Ssn`) REFERENCES `Producer`(`Ssn`);

ALTER TABLE `Consumption_Meter` ADD CONSTRAINT `Consumption_Meter_fk0` FOREIGN KEY (`Consumer_Ssn`) REFERENCES `Consumer`(`Ssn`);

ALTER TABLE `Consumption_Meter` ADD CONSTRAINT `Consumption_Meter_fk1` FOREIGN KEY (`Store_ID`) REFERENCES `Regional_store`(`ID`);

ALTER TABLE `Measurement` ADD CONSTRAINT `Measurement_fk0` FOREIGN KEY (`Pmeter_ID`) REFERENCES `Production_meter`(`Meter_ID`);

ALTER TABLE `Measurement` ADD CONSTRAINT `Measurement_fk1` FOREIGN KEY (`Cmeter_ID`) REFERENCES `Consumption_Meter`(`Meter_ID`);

ALTER TABLE `Bill` ADD CONSTRAINT `Bill_fk0` FOREIGN KEY (`Ssn`) REFERENCES `Customer`(`Ssn`);

ALTER TABLE `Bill` ADD CONSTRAINT `Bill_fk1` FOREIGN KEY (`Contract_ID`) REFERENCES `Contract`(`ID`);

ALTER TABLE `Bill` ADD CONSTRAINT `Bill_fk2` FOREIGN KEY (`Store_ID`) REFERENCES `Regional_store`(`ID`);

ALTER TABLE `Bill` ADD CONSTRAINT `Bill_fk3` FOREIGN KEY (`P_Measurement _ID`) REFERENCES `Measurement`(`ID`);

ALTER TABLE `Bill` ADD CONSTRAINT `Bill_fk4` FOREIGN KEY (`C_Measurement _ID`) REFERENCES `Measurement`(`ID`);

ALTER TABLE `Contract` ADD CONSTRAINT `Contract_fk0` FOREIGN KEY (`Ssn`) REFERENCES `Customer`(`Ssn`);

