from kafka import KafkaConsumer
import pandas as pd
import json, requests, time
import boto3


API_URL="https://zomato-e2e-data-engineering.onrender.com/api"

s3_client=boto3.client(
    's3',
    endpoint_url='http://localhost:9002',
    aws_access_key_id='admin',
    aws_secret_access_key='password123'
)

bucket_names=['food-topic-zomato','menu-topic-zomato','order_items-topic-zomato','restaurants-topic-zomato', 'users-topic-zomato', 'reviews-topic-zomato']
Topic_to_folder={
    'food-topic-zomato':'food',
    'menu-topic-zomato':'menu',
    'order_items-topic-zomato':'order_items',
    'restaurants-topic-zomato':'restaurants',
    'users-topic-zomato':'users',
    'reviews-topic-zomato':'reviews'
}

consumer=KafkaConsumer(*bucket_names,
                       bootstrap_servers='localhost:29092',
                       auto_offset_reset='earliest',
                       enable_auto_commit=True,
                       value_deserializer=lambda v: str(v).decode('utf-8'),
                       group_id='my-zomato-consumer-group')

print('Consumer streaming started! Waiting for Kafka messages...', flush=True)

for message in consumer:
    batch= 1
    topic=message.topic
    data=message.value)
    folder_name=Topic_to_folder.get(topic)
    key=f"{folder_name}/{folder_name}{batch:03d}.json"
