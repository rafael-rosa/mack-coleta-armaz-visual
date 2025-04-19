# dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
import os
path = os.environ['AIRFLOW_HOME']

from datetime import timedelta, datetime

default_args = {
                'owner': 'airflow',
                'depends_on_past': False,
                'email': ['rafael@email.com'],
                'email_on_failure': False,
                'email_on_retry': False,
                'retries': 2,
                'retry_delay': timedelta(minutes=1)
                }

# Define the DAG, its ID and when should it run. Run it every day at 19:00.
dag = DAG(
            dag_id='proj_hist_btc_dag',
            start_date=datetime(year=2025, month=4, day=12, hour=20),
            schedule_interval="0 19 * * *",
            default_args=default_args,
            catchup=False
            )

# Define the task 1 (collect the data) id. Run the bash command because the task is in a .py file.
task1 = BashOperator(
                        task_id='get_btc_dolar_data',
                        bash_command=f'python {path}/dags/src/get_btc_dolar_data.py --num_pages=1',
                        dag=dag
                    )
