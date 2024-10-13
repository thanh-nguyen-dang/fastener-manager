-- Create the 'postgres' role if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT
      FROM   pg_catalog.pg_roles
      WHERE  rolname = 'postgres') THEN

      CREATE ROLE postgres WITH LOGIN PASSWORD 'postgres';
      ALTER ROLE postgres WITH SUPERUSER CREATEDB CREATEROLE REPLICATION;
   END IF;
END
$do$;
