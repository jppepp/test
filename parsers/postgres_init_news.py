import psycopg2
from typing import List, Dict, Tuple, Optional
import sys
from datetime import datetime
from contextlib import contextmanager


class PostgresNewsManager:
    """Класс для управления новостями в PostgreSQL"""

    def __init__(self):
        self.conn_params = {
            'dbname': 'inflation_data',
            'user': 'postgres',
            'password': '123',
            'host': 'localhost',
            'port': '5432'
        }
        self.conn = None

    @contextmanager
    def _get_cursor(self):
        """Контекстный менеджер для работы с курсором"""
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f"Ошибка базы данных: {e}") from e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _ensure_news_table_exists(self) -> bool:
        """Проверяет существование таблицы новостей, создает если нужно"""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("""
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
            return True
        except Exception as e:
            print(f"Ошибка создания таблицы новостей: {e}", file=sys.stderr)
            return False

    def save_news_batch(self, news_list: List[Dict]) -> Tuple[int, int]:
        """
        Сохраняет список новостей в базу данных
        Возвращает кортеж (количество сохраненных, количество дубликатов)
        """
        if not news_list:
            return (0, 0)

        if not self._ensure_news_table_exists():
            return (0, 0)

        saved = 0
        duplicates = 0

        try:
            with self._get_cursor() as cursor:
                for news in news_list:
                    try:
                        cursor.execute("""
                            INSERT INTO news (title, date, link, source)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT ON CONSTRAINT unique_news_item DO NOTHING
                        """, (
                            news.get('title', ''),
                            news.get('date', ''),
                            news.get('link', ''),
                            news.get('source', '')
                        ))
                        if cursor.rowcount > 0:
                            saved += 1
                        else:
                            duplicates += 1
                    except Exception as e:
                        print(f"Ошибка сохранения новости: {e}", file=sys.stderr)
                        continue

                return (saved, duplicates)

        except Exception as e:
            print(f"Критическая ошибка при сохранении новостей: {e}", file=sys.stderr)
            return (0, 0)

    def get_latest_news(self, limit: int = 10) -> Optional[List[Dict]]:
        """Получает последние новости из базы данных"""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("""
                    SELECT title, date, link, source, created_at
                    FROM news 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))

                return [{
                    'title': row[0],
                    'date': row[1],
                    'link': row[2],
                    'source': row[3],
                    'created_at': row[4]
                } for row in cursor.fetchall()]

        except Exception as e:
            print(f"Ошибка получения новостей: {e}", file=sys.stderr)
            return None

    def get_news_statistics(self) -> Optional[Dict]:
        """Возвращает статистику по новостям"""
        try:
            with self._get_cursor() as cursor:
                # Общее количество новостей
                cursor.execute("SELECT COUNT(*) FROM news")
                total = cursor.fetchone()[0]

                # Количество по источникам
                cursor.execute("""
                    SELECT source, COUNT(*) 
                    FROM news 
                    GROUP BY source
                    ORDER BY COUNT(*) DESC
                """)
                by_source = {row[0]: row[1] for row in cursor.fetchall()}

                # Последняя дата обновления
                cursor.execute("SELECT MAX(created_at) FROM news")
                last_update = cursor.fetchone()[0]

                return {
                    'total': total,
                    'by_source': by_source,
                    'last_update': last_update
                }

        except Exception as e:
            print(f"Ошибка получения статистики: {e}", file=sys.stderr)
            return None

    def search_news(self, query: str, limit: int = 10) -> Optional[List[Dict]]:
        """Поиск новостей по ключевым словам"""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("""
                    SELECT title, date, link, source, created_at
                    FROM news 
                    WHERE title ILIKE %s
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (f"%{query}%", limit))

                return [{
                    'title': row[0],
                    'date': row[1],
                    'link': row[2],
                    'source': row[3],
                    'created_at': row[4]
                } for row in cursor.fetchall()]

        except Exception as e:
            print(f"Ошибка поиска новостей: {e}", file=sys.stderr)
            return None


if __name__ == "__main__":
    # Пример использования
    manager = PostgresNewsManager()

    # Тест сохранения новостей
    test_news = [
        {
            'title': 'Тестовая новость 1',
            'date': '2023-01-01',
            'link': 'http://example.com/1',
            'source': 'Test Source'
        },
        {
            'title': 'Тестовая новость 2',
            'date': '2023-01-02',
            'link': 'http://example.com/2',
            'source': 'Test Source'
        }
    ]

    saved, duplicates = manager.save_news_batch(test_news)
    print(f"Сохранено: {saved}, Дубликатов: {duplicates}")

    # Получение новостей
    news = manager.get_latest_news(5)
    print("\nПоследние новости:")
    for item in news:
        print(f"- {item['title']} ({item['source']})")

    # Статистика
    stats = manager.get_news_statistics()
    print("\nСтатистика:")
    print(f"Всего новостей: {stats['total']}")
    print("По источникам:")
    for source, count in stats['by_source'].items():
        print(f"  {source}: {count}")