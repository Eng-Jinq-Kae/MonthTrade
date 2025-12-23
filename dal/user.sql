SELECT current_user; --curent user credential
SELECT usename FROM pg_user; --all PostgreSQL roles (users)
--Schemas → pg_catalog → Views

--Step 1
CREATE USER mthtradeuser
WITH PASSWORD '123';

--Step 2
GRANT CONNECT ON DATABASE "MthTrade" TO "mthtradeuser";

--Step 3
GRANT USAGE ON SCHEMA public TO "mthtradeuser";
GRANT SELECT, INSERT, UPDATE
ON ALL TABLES IN SCHEMA public
TO "mthtradeuser";

--Step 4
ALTER DEFAULT PRIVILEGES
IN SCHEMA public
GRANT SELECT, INSERT, UPDATE
ON TABLES
TO "mthtradeuser";
