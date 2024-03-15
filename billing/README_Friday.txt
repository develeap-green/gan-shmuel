NOTE: The flask app and the DB aren't connected to each other yet, didn't change the code except for adding a home route and some ordering.

How to use the docker-compose to set a MYSQL & Flask containers:

1. docker compose up --build
	It builds and starts both containers named: billing-api-1, billing-db-1

2. To test the flask app: 
	localhost:5000/ or localhost:5000/health

3. To test the DB initialization and creating sample tables:
	docker exec -it billing-db-1 /bin/bash
	docker exec -it billing-db-1 mysql -u root -p
	password: pass

	SHOW databases;
		+--------------------+
		| Database           |
		+--------------------+
		| billing            |
		| information_schema |
		| mysql              |
		| performance_schema |
		| sys                |
		+--------------------+
		5 rows in set (0.00 sec)

	USE billing;

	SHOW tables;
		+-------------------+
		| Tables_in_billing |
		+-------------------+
		| Provider          |
		| Rates             |
		| Trucks            |
		+-------------------+
		3 rows in set (0.00 sec)

	SELECT * FROM Provider;
		+-------+------------+
		| id    | name       |
		+-------+------------+
		| 10001 | Provider 1 |
		| 10002 | Provider 2 |
		| 10003 | Provider 3 |
		+-------+------------+
		3 rows in set (0.00 sec)

If anything doesn't work and you don't see why, contant me!

Roey