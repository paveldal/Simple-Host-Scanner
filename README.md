# Simple Host Scanner

Этот репозиторий содержит код для выполнения домашней работы в рамках интенсива PT 2023 осень (INT-2).

## Установка

### Через Docker (рекомендуется для Debian-подобных систем):

```bash
git clone https://github.com/paveldal/Simple-Host-Scanner.git
cd Simple-Host-Scanner/
docker-compose build
docker-compose up
```

### Через Python (на вашей локальной машине):
Сначала необходимо установить PostgreSQL и создать базу данных:
```git clone https://github.com/paveldal/Simple-Host-Scanner.git
cd Simple-Host-Scanner/
sudo apt-get update
sudo apt-get install postgresql
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE scanner;"
sudo -u postgres psql -c "CREATE USER scanner WITH PASSWORD 'scanner';"
sudo -u postgres psql -c "ALTER ROLE scanner SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE scanner SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE scanner SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE scanner TO scanner;"```

Затем необходимо изменить настройки базы данных в конфигурации проекта:
```vim Scanner/settings.py```
Измените конфигурацию базы данных на:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'scanner',
        'USER': 'scanner',
        'PASSWORD': 'scanner',
        'HOST': 'localhost',  # Или используйте IP вашего сервера PostgreSQL
        'PORT': '5432',
    }
}
```
После настройки базы данных запустите сервер разработки:
```python3 manage.py runserver 127.0.0.1:1337```

Откройте веб-браузер и перейдите по адресу http://127.0.0.1:1337 для доступа к приложению.
