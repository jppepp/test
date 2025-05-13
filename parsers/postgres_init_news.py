import psycopg2
from typing import List, Dict, Tuple, Optional
import sys
from datetime import datetime


class PostgresNewsManager:
    """Управление новостями в PostgreSQL"""

    def __init__(self):
        self.conn = None

    def connect(self) -> bool:
        """Устанавливает соединение с БД"""
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
            print(f"Ошибка подключения к PostgreSQL: {e}", file=sys.stderr)
            return False

    def _ensure_news_table(self) -> bool:
        """Создает или обновляет таблицу новостей"""
        try:
            with self.conn.cursor() as cursor:
                # Удаляем старую таблицу, если она существует
                cursor.execute("DROP TABLE IF EXISTS news")

                # Создаем новую таблицу с актуальной структурой
                cursor.execute("""
                    CREATE TABLE news (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        date TEXT,
                        link TEXT NOT NULL,
                        source TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        CONSTRAINT unique_news_item UNIQUE(link, source)
                    )
                """)
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка создания таблицы новостей: {e}", file=sys.stderr)
            self.conn.rollback()
            return False

    def save_news_batch(self, news_list: List[Dict]) -> Tuple[int, int]:
        """Сохраняет список новостей с проверкой дубликатов"""
        if not news_list:
            return (0, 0)

        if not self._ensure_news_table():
            return (0, 0)

        saved = 0
        duplicates = 0

        try:
            with self.conn.cursor() as cursor:
                for news in news_list:
                    try:
                        cursor.execute("""
                            INSERT INTO news (title, date, link, source)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT ON CONSTRAINT unique_news_item DO NOTHING
                        """, (
                            news['title'],
                            news['date'],
                            news['link'],
                            news['source']
                        ))
                        if cursor.rowcount > 0:
                            saved += 1
                        else:
                            duplicates += 1
                    except psycopg2.Error as e:
                        print(f"Ошибка сохранения новости: {e}", file=sys.stderr)
                        continue

                self.conn.commit()
                return (saved, duplicates)

        except psycopg2.Error as e:
            print(f"Ошибка БД при сохранении новостей: {e}", file=sys.stderr)
            self.conn.rollback()
            return (0, 0)

    def get_latest_news(self, limit: int = 10) -> Optional[List[Dict]]:
        """Получает последние новости"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT title, date, link, source 
                    FROM news 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))

                return [{
                    'title': row[0],
                    'date': row[1],
                    'link': row[2],
                    'source': row[3]
                } for row in cursor.fetchall()]

        except psycopg2.Error as e:
            print(f"Ошибка получения новостей: {e}", file=sys.stderr)
            return None

    def close(self):
        """Закрывает соединение с БД"""
        if self.conn and not self.conn.closed:
            self.conn.close()