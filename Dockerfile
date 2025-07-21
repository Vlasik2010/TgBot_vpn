FROM python:3.11-slim

WORKDIR /app

# System deps for wireguard & psycopg2
RUN apt-get update && \ \
    apt-get install -y --no-install-recommends wireguard-tools libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "vpn_bot"]