#!/bin/sh

# Ожидание доступности Postgres
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Выполнение миграций Django
echo "Running Django migrations"
python manage.py makemigrations
python manage.py migrate --noinput

# Запуск команды, переданной в entrypoint (обычно это запуск веб-сервера)
exec "$@"