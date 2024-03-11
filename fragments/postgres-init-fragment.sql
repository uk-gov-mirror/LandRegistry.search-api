-- Create llc_register database
CREATE DATABASE llc_register;

--Create user for llc_register DB
CREATE ROLE llc_register_user with LOGIN password 'llc_register_password';

\c llc_register;
CREATE EXTENSION postgis;