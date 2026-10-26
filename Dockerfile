FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATA_DIR=/data
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN SECRET_KEY=build-only python manage.py collectstatic --noinput
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/healthz',timeout=3)" || exit 1
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py bootstrap_site && exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --access-logfile -"]
