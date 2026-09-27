from kafka import KafkaConsumer
import pandas as pd
import ast, json, requests, time
import boto3


API_URL="https://zomato-e2e-data-engineering.onrender.com/api"

s3_client=boto3.client(
    's3',
    endpoint_url='http://localhost:9002',
    aws_access_key_id='admin',
    aws_secret_access_key='password123'
)

#bucket_names=['food-topic-zomato','menu-topic-zomato','order_items-topic-zomato','restaurants-topic-zomato', 'users-topic-zomato', 'reviews-topic-zomato']
bucket_names=['food-topic-zomato','menu-topic-zomato','order_items-topic-zomato','restaurants-topic-zomato', 'users-topic-zomato', 'reviews-topic-zomato']

Topic_to_folder={
    'food-topic-zomato':'food',
    'menu-topic-zomato':'menu',
    'order_items-topic-zomato':'order_items',
    'restaurants-topic-zomato':'restaurants',
    'users-topic-zomato':'users',
    'reviews-topic-zomato':'reviews'
}


def deserialize_message(value):
    decoded = value.decode('utf-8')
    try:
        return json.loads(decoded)
    except json.JSONDecodeError:
        # Support messages already queued by the previous str(dict) producer.
        return ast.literal_eval(decoded)


consumer=KafkaConsumer(*bucket_names,
                       bootstrap_servers='localhost:29092',
                       auto_offset_reset='earliest',
                       enable_auto_commit=True,
                       value_deserializer=deserialize_message,
                       group_id='my-zomato-consumer-group')

print('Consumer streaming started! Waiting for Kafka messages...', flush=True)

for message in consumer:
    topic=message.topic
    folder_name=Topic_to_folder.get(topic)
    data=message.value
    key=f"{folder_name}/{folder_name}-p{message.partition}-{message.offset + 1:06d}.json"
    print(f'Received message for {topic} at {time.time()}. Uploading to MinIO...', flush=True)

    minio_bucket_name='zomato-bronze-transaction'
    try:
        s3_client.put_object(
            Bucket=minio_bucket_name,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        print('Saved batch for topic:', topic, 'at timestamp:', time.time(), 'to S3 bucket:', minio_bucket_name, 'with key:', key, flush=True)
    except Exception as e:
            print(f'Failed to upload {key} to S3: {e}', flush=True)
            continue