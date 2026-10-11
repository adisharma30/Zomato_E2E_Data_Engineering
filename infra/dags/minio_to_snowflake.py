import os
import boto3
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "password123"
BUCKET = "zomato-bronze-transaction"
LOCAL_DIR = "C:/Users/91787/Python_Repo/Zomato_E2E_Data_Engineering/tmp/minio_downloads"

SNOWFLAKE_USER = "ADISHARMA"
SNOWFLAKE_PRIVATE_KEY_PATH = "/opt/airflow/secrets/rsa_key.p8"
SNOWFLAKE_ACCOUNT = "oc33285.eu-central-1"
SNOWFLAKE_WAREHOUSE = "ZOMATO_WH"
SNOWFLAKE_DB = "ZOMATO"
SNOWFLAKE_SCHEMA = "COMMON"