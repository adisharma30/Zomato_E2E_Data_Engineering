from kafka import KafkaProducer
from kafka.errors import KafkaError
import pandas as pd
import requests
import json, time

API_URL='https://zomato-e2e-data-engineering.onrender.com/api'
#categories = ['restaurant', 'food', 'menu', 'order_items', 'users', 'reviews', 'orders']
categories = ['users']
try:
    producer=KafkaProducer(bootstrap_servers='localhost:29092',
                           value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                           max_block_ms=5000)
except Exception as e:
    print(f"Error connecting to Kafka: {e}")
    exit(1)
  
print("Producer started successfully!", flush=True)

def fetch_data_zomato(category,page,limit=1000):
    url=f'{API_URL}/{category}/'
    query_paramaters={"page":page,
                          "limit":limit}
    try:
        response=requests.get(url,params=query_paramaters)
        response.raise_for_status()
        data=response.json()
        data['category_data']=category
        data['timestamp']=int(time.time())
        return data
    except Exception as e:
        print(f"Error occured for {category}: {e}")
        return None

while True:
    print(f"Starting fetch cycle at {time.time()}", flush=True)
    for cat in categories:
        page=1
        print(f"Fetching data for {cat}")
        while True:
            resp=fetch_data_zomato(cat,page)
            if not resp or not resp.get('data'):
                break
            if resp:
                try:
                    producer.send(f"{cat}-topic-zomato", value=resp).get(timeout=5)
                except KafkaError as e:
                    print(
                        f"Kafka could not accept data for {cat} page {page}: {e}. "
                        "Skipping this category for the current cycle.",
                        flush=True
                    )
                    break
                print(f"Sent data for {cat}:{page}:{resp}", flush=True)
                page+=1
                time.sleep(0.2)