-- schema.sql


DROP DATABASE IF EXISTS waldoDB;
CREATE DATABASE waldoDB;
\c waldoDB;

CREATE TABLE m_user 
(
user_id SERIAL,
full_name character varying,
email character varying,
hash_password character varying,
mobile_number character varying,
user_name character varying ,
UNIQUE (user_name)
);

CREATE TABLE b_user_preference
(
user_id integer,
preference_json json
);

CREATE TABLE category
(
cat_json json
);