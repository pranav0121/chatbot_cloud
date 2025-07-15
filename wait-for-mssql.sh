#!/bin/bash
# Wait for MSSQL to be ready before starting the app
set -e

host="$1"
shift

until nc -z "$host" 1433; do
  >&2 echo "MSSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "MSSQL is up - executing command"
exec "$@"
