from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
import os, datetime         
import requests
from airflow.decorators import task,dag
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pendulum 
@dag(
        dag_id="create_employees_table_dag",
        schedule="0 0 * * *",
        start_date=pendulum.datetime(2026, 10, 12, tz="UTC"),
        catchup=False,
        dagrun_timeout=datetime.timedelta(minutes=60),
)
def process_employee_data():
    create_employees_table=SQLExecuteQueryOperator(
        task_id="create_employees_table_scratch",
        conn_id="tutorial_pg_conn",
        sql="""
        CREATE TABLE IF NOT EXISTS employees ("Serial Number" NUMERIC PRIMARY KEY,
                "Company Name" TEXT,
                "Employee Markme" TEXT,
                "Description" TEXT,
                "Leave" INTEGER
                );"""
    )

    create_temp_employee_table= SQLExecuteQueryOperator(
        task_id="create_temp_employee_table",
        conn_id="tutorial_pg_conn",
        sql="""
        CREATE TABLE IF NOT EXISTS temp_employees ("Serial Number" NUMERIC PRIMARY KEY,
                "Company Name" TEXT,
                "Employee Markme" TEXT,
                "Description" TEXT,
                "Leave" INTEGER
                );"""
    )

    @task()
    def get_data():
        path = os.path.join(os.path.dirname(__file__), "files", "employees.csv")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        url='https://raw.githubusercontent.com/apache/airflow/main/airflow-core/docs/tutorial/pipeline_example.csv'

        response=requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(path, 'w') as f:
            f.write(response.text)
        postreshook=PostgresHook(postgres_conn_id="tutorial_pg_conn")
        postreshook.copy_expert("COPY temp_employees FROM STDIN WITH CSV HEADER DELIMITER AS ',' QUOTE AS '\"'", path)

    @task()
    def merge_data():
        query="""INSERT INTO employees 
        select * from (
        select distinct * from
        temp_employees ) t  
        on conflict ("Serial Number") do update 
        set  "Employee Markme" = excluded."Employee Markme",
                "Description" = excluded."Description",
                "Leave" = excluded."Leave" """
        try:
            postreshook=PostgresHook(postgres_conn_id="tutorial_pg_conn")
            conn=postreshook.get_conn()
            cur=conn.cursor()
            cur.execute(query)
            conn.commit()
            return 0
        except Exception as e:
            print(f"Error occurred: {e}")   
            return 1
    get_data= get_data()
    merge_data= merge_data()
    create_employees_table >> create_temp_employee_table >> get_data >> merge_data

dag = process_employee_data()

