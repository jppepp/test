import psycopg2
from psycopg2 import sql
import sys

def create_database():
    """Создает базу данных и необходимые таблицы"""
    try:
        # Подключаемся к системной БД postgres
        sys_conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
        )
        sys_conn.autocommit = True
        sys_cursor = sys_conn.cursor()

        # Проверяем существование БД
        sys_cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'inflation_data'")
        if not sys_cursor.fetchone():
            # Создаем БД с правильной кодировкой
            sys_cursor.execute("""
                CREATE DATABASE inflation_data
                WITH 
                    TEMPLATE = template0
                    ENCODING = 'UTF8'
                    LC_COLLATE = 'ru_RU.UTF-8'
                    LC_CTYPE = 'ru_RU.UTF-8'
            """)
            print("База данных 'inflation_data' создана")

        sys_cursor.close()
        sys_conn.close()

        # Теперь подключаемся к нашей БД и создаем таблицы
        app_conn = psycopg2.connect(
            dbname="inflation_data",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
        )
        app_cursor = app_conn.cursor()

        # Создаем таблицы
        app_cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        app_cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_types (
                id SERIAL PRIMARY KEY,
                type_name VARCHAR(50) NOT NULL UNIQUE,
                is_official BOOLEAN DEFAULT FALSE
            )
        """)

        app_cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                url VARCHAR(255)
            )
        """)

        app_cursor.execute("""
            CREATE TABLE IF NOT EXISTS inflation_rates (
                id SERIAL PRIMARY KEY,
                country_id INTEGER NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
                year INTEGER NOT NULL,
                data_type_id INTEGER NOT NULL REFERENCES data_types(id) ON DELETE RESTRICT,
                rate DECIMAL(10,2) NOT NULL,
                source VARCHAR(255),
                last_updated TIMESTAMP DEFAULT NOW(),
                UNIQUE(country_id, year, data_type_id)
            )
        """)

        app_cursor.execute("""
            CREATE TABLE IF NOT EXISTS inflation_data_sources (
                inflation_rate_id INTEGER NOT NULL REFERENCES inflation_rates(id) ON DELETE CASCADE,
                source_id INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
                PRIMARY KEY (inflation_rate_id, source_id)
            )
        """)

        app_cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                date TEXT,
                link TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT unique_news_item UNIQUE(link, source)
            )
        """)

        # Добавляем стандартные данные
        app_cursor.execute("""
            INSERT INTO data_sources (name, url)
            VALUES 
                ('Inflation.eu', 'https://www.inflation.eu'),
                ('Trading Economics', 'https://tradingeconomics.com')
            ON CONFLICT (name) DO NOTHING
        """)

        app_conn.commit()
        print("Таблицы успешно созданы")

    except psycopg2.Error as e:
        print(f"Ошибка при создании базы данных: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'app_cursor' in locals():
            app_cursor.close()
        if 'app_conn' in locals():
            app_conn.close()

if __name__ == "__main__":
    create_database()