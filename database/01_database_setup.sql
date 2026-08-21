/*
================================================
DATABASE INITIALIZATION
================================================
*/

SELECT current_database();


CREATE SCHEMA IF NOT EXISTS recruitment;


SELECT schema_name
FROM information_schema.schemata;