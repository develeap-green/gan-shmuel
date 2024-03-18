How to use the docker-compose to set a MYSQL & Flask containers:

1. docker compose up --build
	It builds and starts both containers named: billing-api-1, billing-db-1

2. To test the flask app: 
	localhost:5000/health

3. To test the DB and print its contents:
    localhost:5000/tables

4. To test the routes use Postman.
   Example:
        URL: http://localhost:5000/provider
        Method: POST
        Body (raw JSON):
            {
              "name": "New Provider"
            }

5. To MANUALLY test the DB initialization and creating sample tables:
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

Roey