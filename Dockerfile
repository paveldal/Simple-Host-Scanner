FROM python:3.11
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DJANGO_SETTINGS_MODULE=Scanner.settings
ENV PYTHONUNBUFFERED=1
EXPOSE 1337
CMD ["python", "manage.py", "runserver", "0.0.0.0:1337"]
CMD ["python", "manage.py", "migrate"]
