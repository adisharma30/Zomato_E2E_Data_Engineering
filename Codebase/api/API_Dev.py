import pandas as pd
import numpy as np
import requests
from fastapi import FastAPI
import os


app=FastAPI()

dataframes={}
base_path= 'C:/Users/91787/Python_Repo/Zomato_E2E_Data_Engineering/data'
files=['food','menu','order_items','restaurant','users','reviews']

def read_csv_file(file_path):
    """
    Reads a CSV file and returns a pandas DataFrame.
    
    Args:
        file_path (str): The path to the CSV file."""
    try:
        df=pd.read_csv(file_path)
        df = df.replace({np.nan: None})
        return df
    
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

for file in files:
    path=os.path.join(base_path,f"{file}.csv")
    dataframes[f'{file}_df']= read_csv_file(path)

@app.get("/api/food/")
def get_food_data(page: int = 1, limit: int = 100):
    food_df = dataframes.get('food_df')
    if food_df  is not None:
        start = (page - 1) * limit
        end = start + limit
        return food_df.iloc[start:end].to_dict(orient="records")
    else:
        return {"error": "File not found"}

@app.get("/api/menu/")
def get_menu_data(page: int = 1, limit: int = 100):
    menu_df = dataframes.get('menu_df')
    if menu_df is not None:
        start = (page - 1) * limit
        end = start + limit
        return menu_df.iloc[start:end].to_dict(orient='records')
    else:
        return {"error": "File not found"}

@app.get("/api/order_items/")
def get_order_items_data( page:int=1, limit:int=100):
    order_items_df   = dataframes.get('order_items_df')
    start = (page - 1) * limit
    end = start + limit
    if order_items_df is not None:
        return order_items_df.iloc[start:end].to_dict(orient='records')
    else:
        return None

@app.get("/api/restaurant/")
def get_restaurant_data(page: int = 1, limit: int = 100):
    restaurant_df = dataframes.get('restaurant_df')
    if restaurant_df is not None:
        start = (page - 1) * limit
        end = start + limit
        return restaurant_df.iloc[start:end].to_dict(orient='records')
    else:
        return {"error": "File not found"}

@app.get("/api/users/")
def get_users_data(page: int = 1, limit: int = 100):
    users_df = dataframes.get('users_df')
    if users_df is not None:
        start = (page - 1) * limit
        end = start + limit
        users = users_df.iloc[start:end].drop(columns=['password'], errors='ignore')
        return users.to_dict(orient='records')
    else:
        return {"error": "File not found"}

@app.get("/api/reviews/")
def get_reviews_data(page: int = 1, limit: int = 100):
    reviews_df = dataframes.get('reviews_df')
    if reviews_df is not None:
        start = (page - 1) * limit
        end = start + limit
        return reviews_df.iloc[start:end].to_dict(orient='records')
    else:
        return {"error": "File not found"}


