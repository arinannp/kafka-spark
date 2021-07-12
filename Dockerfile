# Use an official Python runtime as a parent image
FROM python:3.7-slim

WORKDIR /python-producer
ADD ./code/kafka_data_producer.py /python-producer/kafka_data_producer.py

COPY requirements.txt ./
RUN pip install -r requirements.txt

ENV BOOTSTRAP_SERVER=kafka:9092
ENV TOPIC_NAME=user_access

CMD ["python", "kafka_data_producer.py"]