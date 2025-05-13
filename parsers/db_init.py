import psycopg2
import sys

def init_db():
    """Инициализация подключения к PostgreSQL"""
    try:
        conn = psycopg2.connect(
            dbname="inflation_data",
            user="postgres",
            password="1111",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к PostgreSQL: {e}", file=sys.stderr)
        raise