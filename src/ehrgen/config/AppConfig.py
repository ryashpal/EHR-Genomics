import os


fhir_server_base_url = 'http://10.172.235.4:8080/fhir'

db_details = {
    "sql_host_name": os.environ['POSTGRES_HOSTNAME'],
    "sql_port_number": os.environ['POSTGRES_PORT_NUMBER'],
    "sql_user_name": os.environ['POSTGRES_USER_NAME'],
    "sql_password": os.environ['POSTGRES_PASSWORD'],
    "sql_db_name": 'omop_alfred',
}
