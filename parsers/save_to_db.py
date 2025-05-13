from db_init import init_db
import sys

def save_to_postgres(rate, year, country, data_type, source=None):
    """Сохраняет данные инфляции в PostgreSQL"""
    conn = None
    try:
        conn = init_db()
        with conn.cursor() as cursor:
            # Вставляем или получаем country_id
            cursor.execute("""
                INSERT INTO countries (name) 
                VALUES (%s) 
                ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
            """, (country,))
            country_id = cursor.fetchone()[0]

            # Вставляем или получаем data_type_id
            cursor.execute("""
                INSERT INTO data_types (type_name, is_official)
                VALUES (%s, %s)
                ON CONFLICT (type_name) DO UPDATE SET type_name = EXCLUDED.type_name
                RETURNING id
            """, (data_type, data_type in ['CPI Inflation', 'PPI Inflation']))
            data_type_id = cursor.fetchone()[0]

            # Вставляем или обновляем данные инфляции
            cursor.execute("""
                INSERT INTO inflation_rates 
                (country_id, year, data_type_id, rate, source)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (country_id, year, data_type_id) 
                DO UPDATE SET 
                    rate = EXCLUDED.rate,
                    source = EXCLUDED.source,
                    last_updated = NOW()
            """, (country_id, year, data_type_id, float(rate), source))

            conn.commit()
    except Exception as e:
        print(f"Ошибка при сохранении данных в PostgreSQL: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()