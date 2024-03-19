# First stage: Build stage
FROM python:3.10 AS builder

WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Second stage: Runtime stage
FROM python:3.10-slim

WORKDIR /app

# Copy dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

RUN mkdir logs

# Copy the source code
COPY . .

EXPOSE 5000

CMD ["python", "./billing.py"]