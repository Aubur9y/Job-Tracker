from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Function to be executed by the PythonOperator
def print_hello():
    print("Hello, Airflow!")

# Define the DAG
with DAG(
    'simple_hello_dag',
    default_args=default_args,
    description='A simple DAG to test Airflow',
    schedule_interval=timedelta(minutes=10),  # Runs every 10 minutes
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:

    # Define a single task
    hello_task = PythonOperator(
        task_id='say_hello',
        python_callable=print_hello,
    )

    # Add the task to the DAG
    hello_task
