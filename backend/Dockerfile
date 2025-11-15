FROM python:3.11-slim

WORKDIR /app/backend
COPY requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# copy project code
COPY . /app/backend/

# collectstatic placeholder (safe)
RUN mkdir -p /app/backend/static && chmod -R 777 /app/backend/static

EXPOSE 8000

CMD ["gunicorn", "price_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
