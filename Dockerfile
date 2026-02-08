FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#instala o gunicorn separado
RUN pip install --no-cache-dir gunicorn

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
