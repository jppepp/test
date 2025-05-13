import psycopg2
import sys

class DataNormalizer:
    def __init__(self):
        self.conn = None

    def connect(self) -> bool:
        try:
            self.conn = psycopg2.connect(
                dbname="inflation_data",
                user="postgres",
                password="1111",
                host="localhost",
                port="5432"
            )
            return True
        except psycopg2.Error as e:
            print(f"Ошибка подключения: {e}", file=sys.stderr)
            return False

    def normalize_data(self) -> bool:
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE data_types 
                    SET is_official = TRUE
                    WHERE type_name IN ('CPI Inflation', 'PPI Inflation')
                """)
                self.conn.commit()
                print("Данные успешно нормализованы")
                return True

        except psycopg2.Error as e:
            print(f"Ошибка нормализации: {e}", file=sys.stderr)
            self.conn.rollback()
            return False
        except Exception as e:
            print(f"Неожиданная ошибка при нормализации: {e}", file=sys.stderr)
            return False

    def close(self):
        if self.conn and not self.conn.closed:
            try:
                self.conn.close()
            except Exception as e:
                print(f"Ошибка при закрытии соединения: {e}", file=sys.stderr)

def normalize_inflation_data() -> bool:
    normalizer = DataNormalizer()
    try:
        if not normalizer.connect():
            return False
        return normalizer.normalize_data()
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        return False
    finally:
        normalizer.close()