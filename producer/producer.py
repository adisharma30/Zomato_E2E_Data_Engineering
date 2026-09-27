from kafka import KafkaProducer
import pandas as pd
import requests
import os, time


API_URL='https://zomato-e2e-data-engineering.onrender.com/api'
categories = ['food','menu','order_items','restaurants', 'users', 'reviews']

try:
    producer=KafkaProducer(bootstrap_servers='localhost:9092',
                           value_serializer=lambda v: str(v).encode('utf-8'))
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
        print("Error occured for {category}: {e}")
        return None

while True:
    print(f"Starting fetch cycle at {time.time()}", flush=True)
    for cat in categories:
        page=1
        print(f"Fetching data for {cat}")
        resp=fetch_data_zomato(cat,page,limit=1000)
        if not resp:
            break
        if resp:
            producer.send(f"{cat}-topic-zomato", value=resp)
            print(f"Sent data for {cat}:{page}:{resp}", flush=True)
            page+=1
            time.sleep(1)
        







