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

# Set Flask environment variables
ENV FLASK_APP=billing.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

EXPOSE 5000

# Use Flask's built-in server
ENTRYPOINT ["flask", "run"]