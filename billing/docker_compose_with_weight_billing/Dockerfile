FROM python:3.10

WORKDIR /app

RUN mkdir logs

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "./billing.py"]