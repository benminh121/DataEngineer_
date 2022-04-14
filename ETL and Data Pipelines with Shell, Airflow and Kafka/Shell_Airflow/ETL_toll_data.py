# import the libraries

from datetime import timedelta
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to write tasks!
from airflow.operators.bash_operator import BashOperator
# This makes scheduling easy
from airflow.utils.dates import days_ago

#defining DAG arguments

# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'Ben Nguyen',
    'start_date': days_ago(0),
    'email': ['nguyenthaiminh1201@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# defining the DAG

# define the DAG
dag = DAG(
    'ETL_toll_data',
    default_args=default_args,
    description='ETL_toll_data',
    schedule_interval=timedelta(days=1),
)

# define the tasks

# define the task 'unzip_data'

unzip_data = BashOperator(
    task_id='unzip_data',
    bash_command='wget  "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Final%20Assignment/tolldata.tgz" && tar -xf tolldata.tgz -C $AIRFLOW_HOME/dags/finalassignment/',
    dag=dag,
)

# define the task 'extract_data_from_csv'

extract_data_from_csv = BashOperator(
    task_id='extract_data_from_csv',
    bash_command='cut -f1-4 -d"," vehicle-data.csv > csv_data.csv',
    dag=dag,
)

# define the task 'extract_data_from_tsv'

extract_data_from_tsv = BashOperator(
    task_id='extract_data_from_tsv',
    bash_command='cut -f5-7 tollplaza-data.tsv > tmp_csv.csv && tr "\t" "," <tmp_csv.csv> tsv_data.csv',
    dag=dag,
)

# define the task 'extract_data_from_fixed_width'

extract_data_from_fixed_width = BashOperator(
    task_id='extract_data_from_fixed_width',
    bash_command='cut -c58- payment-data.txt > tmp_txt1.txt && tr " " "," <tmp.txt> tmp_txt2.txt && cut -f2,3 -d"," tmp_txt2.txt > fixed_width_data.csv',
    dag=dag,
)

# define the task 'consolidate_data'

consolidate_data = BashOperator(
    task_id='consolidate_data',
    bash_command='paste -d"," csv_data.csv tsv_data.csv fixed_width_data.csv > extracted_data.csv',
    dag=dag,
)

# define the task 'transform_data'

transform_data = BashOperator(
    task_id='transform_data',
    bash_command="awk -F',' 'BEGIN{OFS=',';}''{print $1,$2,$3,toupper($4),$5,$6,$7,$8,$9;}' extracted_data.csv > transformed_data.csv",
    dag=dag,
)

# task pipeline
unzip_data >> extract_data_from_csv >> extract_data_from_tsv >> extract_data_from_fixed_width >> consolidate_data >> transform_data