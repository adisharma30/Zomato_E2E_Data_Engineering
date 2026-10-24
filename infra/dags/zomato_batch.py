from datetime import datetime
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.bash import BashOperator

DBT_PROJECT= '/opt/airflow/dbt_zomato'
DBT_PROFILES_DIR = '/opt/airflow/secrets'
DBT= '/opt/dbt-venv/bin/dbt'

COPY_RAW=[
    "USE WAREHOUSE ZOMATO_WH",
    "COPY INTO RAW.RESTAURANTS FROM @ZOMATO.RAW.MINIO_ZOMATO_UPLOAD/restaurant ON_ERROR ='CONTINUE'",
    "COPY INTO RAW.MENU FROM @ZOMATO.RAW.MINIO_ZOMATO_UPLOAD/menu ON_ERROR ='CONTINUE'",
    "COPY INTO RAW.ORDERS FROM @ZOMATO.RAW.MINIO_ZOMATO_UPLOAD/orders ",
    "COPY INTO RAW.FOOD FROM @ZOMATO.RAW.MINIO_ZOMATO_UPLOAD/FOOD ON_ERROR ='CONTINUE'",
    "COPY INTO RAW.USERS FROM @ZOMATO.RAW.MINIO_ZOMATO_UPLOAD/users ON_ERROR ='CONTINUE'",
    "COPY INTO RAW.ORDER_ITEMS FROM @ZOMATO.RAW.MINIO_ZOMATO_UPLOAD/order_items ",
    "COPY INTO RAW.REVIEWS FROM @ZOMATO.RAW.MINIO_ZOMATO_UPLOAD/reviews ",    

]

with DAG(
    dag_id='zomato_batch',
    start_date=datetime(2026, 10, 23),
    schedule_interval='@daily',
    catchup=False,
    tags=['zomato','batch','dbt']

) as dag:

    # reload_raw= SQLExecuteQueryOperator(
    #     task_id='reload_raw',
    #     conn_id='snowflake_adi',
    #     sql=COPY_RAW,
    #     split_statements=True,
    #     autocommit= True,
    # )

    dbt_build= BashOperator(
        task_id='dbt_build_run',
        bash_command=(
            f"{DBT} build --project-dir {DBT_PROJECT} "
            f"--profiles-dir {DBT_PROFILES_DIR}"
        )

    )

    dbt_build