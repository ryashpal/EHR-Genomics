import os


fhir_server_base_url = 'http://superbugai.erc.monash.edu:8082/fhir'

db_details = {
    "sql_host_name": os.environ['POSTGRES_HOSTNAME'],
    "sql_port_number": os.environ['POSTGRES_PORT_NUMBER'],
    "sql_user_name": os.environ['POSTGRES_USER_NAME'],
    "sql_password": os.environ['POSTGRES_PASSWORD'],
    "sql_db_name": os.environ['POSTGRES_DB_NAME'],
}
