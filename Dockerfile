FROM python:3.12

WORKDIR /app

RUN pip install requests

COPY auto_label.py .
