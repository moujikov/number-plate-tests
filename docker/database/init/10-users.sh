#!/bin/bash

set -eu -o pipefail

create_user() {
	local USER=$1
	local PASSWORD="$(< /run/secrets/db_password_$USER)"

	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
		CREATE USER $USER WITH PASSWORD '$PASSWORD';
		GRANT CONNECT ON DATABASE $POSTGRES_DB TO $USER;
		GRANT USAGE ON SCHEMA public TO $USER;
		ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO $USER;
		ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO $USER;
	EOSQL
}

create_user processor
create_user skud
create_user frontend
