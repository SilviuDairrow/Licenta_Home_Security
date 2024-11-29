FROM python:3.9-slim

WORKDIR /app

COPY ./dockerfiles/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "Server:app", "--host", "0.0.0.0", "--port", "8000"]
