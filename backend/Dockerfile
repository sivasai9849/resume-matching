FROM python:3.10-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update -y && \
    apt-get install -y gcc python3-dev && \
    apt-get clean

COPY requirements.txt /app

RUN pip install --upgrade pip wheel setuptools
RUN pip install --no-binary=:all: docx2txt Flask-Principal Flask-Script
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Chmod to entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
