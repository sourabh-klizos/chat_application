FROM python:3.11-slim

WORKDIR /mnt/locust

COPY . .

RUN pip install locust websocket-client pymongo

CMD ["locust"]