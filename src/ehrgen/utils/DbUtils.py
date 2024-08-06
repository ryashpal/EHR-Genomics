from src.ehrgen.config import AppConfig

import psycopg2
import pandas as pd


def getConnection():

    # Connect to postgres with a copy of the MIMIC-III database
    con = psycopg2.connect(
        dbname=AppConfig.db_details["sql_db_name"],
        user=AppConfig.db_details["sql_user_name"],
        host=AppConfig.db_details["sql_host_name"],
        port=AppConfig.db_details["sql_port_number"],
        password=AppConfig.db_details["sql_password"]
        )

    return con


def readDbFromSql(sqlFilePath, params=None):

    sqlFile = open(sqlFilePath)
    query = sqlFile.read().format(params)

    con = getConnection()
    df = pd.read_sql_query(query, con)
    return df


def readDbFromSql(sqlFilePath, params=None):

    sqlFile = open(sqlFilePath)
    query = sqlFile.read()

    con = getConnection()
    df = pd.read_sql_query(query, con)
    return df


def updateDb(sqlQuery, params):
    con = getConnection()
    cur = con.cursor()
    cur.execute(sqlQuery, params)
    count = cur.rowcount
    con.commit()
    return count