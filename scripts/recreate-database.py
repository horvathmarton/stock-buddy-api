from os import getenv

from dotenv import load_dotenv
from psycopg2 import connect, extensions, sql

load_dotenv('environments/development.env')

connection = connect(
    host=getenv('DATABASE_HOST'),
    user=getenv('DATABASE_USER'),
    password=getenv('DATABASE_PASSWORD'),
    dbname='postgres',
)
connection.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cursor = connection.cursor()

cursor.execute(sql.SQL(f"DROP DATABASE IF EXISTS {getenv('DATABASE_NAME')}"))
cursor.execute(sql.SQL(f"CREATE DATABASE {getenv('DATABASE_NAME')}"))

connection.close()

connection = connect(
    host=getenv('DATABASE_HOST'),
    user=getenv('DATABASE_USER'),
    password=getenv('DATABASE_PASSWORD'),
    dbname=getenv('DATABASE_NAME'),
)

with connection:
    cursor = connection.cursor()

    cursor.execute(sql.SQL(f"CREATE SCHEMA raw_data"))
    cursor.execute(sql.SQL(f"CREATE SCHEMA stocks"))
    cursor.execute(sql.SQL(f"CREATE SCHEMA transactions"))
