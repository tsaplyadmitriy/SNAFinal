#!/bin/sh
# wait-for-postgres.sh

set -e
  

cmd="$@"
  
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U"$POSTGRES_USER" $POSTGRES_DB -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done
  
>&2 echo "Postgres is up - executing command"

if [ "$SKIP_MIGRATION" = "True" ] ; then 
  echo "Skip migration..."; 
else
  echo "Run python manage.py migrate..." ;
  python manage.py migrate ;
fi
exec $cmd

