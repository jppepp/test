import psycopg2
import sys

class PostgresManager:
    def __init__(self):
        self.conn = None

    def connect(self) -> bool:
        try:
            self.conn = psycopg2.connect(
                dbname="inflation_data",
                user="postgres",
                password="123",
                host="localhost",
                port="5432"
            )
            return True
        except psycopg2.Error as e:
            print(f"Ошибка подключения к PostgreSQL: {e}", file=sys.stderr)
            return False

    def create_tables(self) -> bool:
        try:
            with self.conn.cursor() as cursor:
                # Удаляем таблицы, если они существуют
                cursor.execute("DROP TABLE IF EXISTS inflation_data_sources CASCADE")
                cursor.execute("DROP TABLE IF EXISTS inflation_rates CASCADE")
                cursor.execute("DROP TABLE IF EXISTS data_sources CASCADE")
                cursor.execute("DROP TABLE IF EXISTS data_types CASCADE")
                cursor.execute("DROP TABLE IF EXISTS countries CASCADE")

                # Создаем таблицы
                cursor.execute("""
                    CREATE TABLE countries (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                cursor.execute("""
                    CREATE TABLE data_types (
                        id SERIAL PRIMARY KEY,
                        type_name VARCHAR(50) NOT NULL UNIQUE,
                        is_official BOOLEAN DEFAULT FALSE
                    )
                """)

                cursor.execute("""
                    CREATE TABLE data_sources (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        url VARCHAR(255)
                    )
                """)

                cursor.execute("""
                    CREATE TABLE inflation_rates (
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

                cursor.execute("""
                    CREATE TABLE inflation_data_sources (
                        inflation_rate_id INTEGER NOT NULL REFERENCES inflation_rates(id) ON DELETE CASCADE,
                        source_id INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
                        PRIMARY KEY (inflation_rate_id, source_id)
                    )
                """)

                # Добавляем стандартные источники данных
                cursor.execute("""
                    INSERT INTO data_sources (name, url)
                    VALUES 
                        ('Inflation.eu', 'https://www.inflation.eu'),
                        ('Trading Economics', 'https://tradingeconomics.com')
                    ON CONFLICT (name) DO NOTHING
                """)

                self.conn.commit()
                return True

        except psycopg2.Error as e:
            print(f"Ошибка при создании таблиц: {e}", file=sys.stderr)
            self.conn.rollback()
            return False

    def close(self):
        if self.conn and not self.conn.closed:
            try:
                self.conn.close()
            except Exception as e:
                print(f"Ошибка при закрытии соединения: {e}", file=sys.stderr)

def init_postgres_tables() -> bool:
    """Инициализирует таблицы в PostgreSQL"""
    manager = PostgresManager()
    try:
        if not manager.connect():
            return False
        return manager.create_tables()
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        return False
    finally:
        manager.close()