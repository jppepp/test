from get_html import get_html
from parse_inflation_data import parse_inflation_data
from parsers import (
    parse_ppi_data,
    parse_cpi_housing_utilities,
    parse_cpi_transportation,
    parse_food_inflation
)
from save_to_db import save_to_postgres
from postgres_init import init_postgres_tables
from normalization import normalize_inflation_data
from news_parser import collect_all_news
from postgres_init_news import PostgresNewsManager
import sys

def collect_inflation_data():
    """Сбор данных по инфляции"""
    countries = ['Brazil', 'China', 'Russia', 'Indonesia', 'India']
    years = list(range(2015, 2026))

    data_sources = {
        'PPI Inflation': {
            'url': 'https://tradingeconomics.com/{}/producer-prices',
            'parser': parse_ppi_data,
            'source': 'Trading Economics'
        },
        'CPI Housing Utilities': {
            'url': 'https://tradingeconomics.com/{}/cpi-housing-utilities',
            'parser': parse_cpi_housing_utilities,
            'source': 'Trading Economics'
        },
        'CPI Transportation': {
            'url': 'https://tradingeconomics.com/{}/cpi-transportation',
            'parser': parse_cpi_transportation,
            'source': 'Trading Economics'
        },
        'Food Inflation': {
            'url': 'https://tradingeconomics.com/{}/food-inflation',
            'parser': parse_food_inflation,
            'source': 'Trading Economics'
        }
    }

    for country in countries:
        print(f"\nСбор данных для {country}:")

        for data_type, config in data_sources.items():
            url = config['url'].format(country.lower())
            try:
                html = get_html(url)
                if html:
                    rate = config['parser'](html)
                    try:
                        save_to_postgres(
                            rate=rate if rate is not None else 0,
                            year=2025,
                            country=country,
                            data_type=data_type,
                            source=config['source']
                        )
                        print(f"{data_type}: {rate if rate is not None else 0}%")
                    except Exception as e:
                        print(f"Ошибка сохранения {data_type}: {e}", file=sys.stderr)
                else:
                    print(f"{data_type}: данные недоступны", file=sys.stderr)
            except Exception as e:
                print(f"Ошибка обработки {data_type}: {e}", file=sys.stderr)

        for year in years:
            url = f"https://www.inflation.eu/en/inflation-rates/{country.lower()}/historic-inflation/cpi-inflation-{country.lower()}-{year}.aspx"
            try:
                html = get_html(url)
                if html:
                    inflation_rate = parse_inflation_data(html)
                    if inflation_rate is not None:
                        try:
                            save_to_postgres(
                                rate=inflation_rate,
                                year=year,
                                country=country,
                                data_type='CPI Inflation',
                                source='Inflation.eu'
                            )
                            print(f"Инфляция за {year}: {inflation_rate}%")
                        except Exception as e:
                            print(f"Ошибка сохранения данных за {year}: {e}", file=sys.stderr)
                    else:
                        print(f"Нет данных за {year}", file=sys.stderr)
                else:
                    print(f"Не удалось получить данные за {year}", file=sys.stderr)
            except Exception as e:
                print(f"Ошибка обработки данных за {year}: {e}", file=sys.stderr)

def display_statistics():
    """Выводит статистику по новостям"""
    manager = PostgresNewsManager()
    try:
        if not manager.connect():
            print("Ошибка подключения к БД", file=sys.stderr)
            return

        # Статистика по источникам
        with manager.conn.cursor() as cursor:
            cursor.execute("""
                SELECT source, COUNT(*) as count 
                FROM news 
                GROUP BY source
                ORDER BY count DESC
            """)
            print("\n=== Статистика новостей ===")
            for source, count in cursor.fetchall():
                print(f"{source}: {count} новостей")

        # Последние 5 новостей
        with manager.conn.cursor() as cursor:
            cursor.execute("""
                SELECT title, date, link, source 
                FROM news 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            print("\n=== Последние новости ===")
            for idx, (title, date, link, source) in enumerate(cursor.fetchall(), 1):
                print(f"\n{idx}. [{source}] {title}")
                print(f"   Дата: {date}")
                print(f"   Ссылка: {link}")

    except Exception as e:
        print(f"Ошибка получения статистики: {e}", file=sys.stderr)
    finally:
        manager.close()

def main():
    print("=== Система мониторинга экономических данных ===")

    # Инициализация таблиц PostgreSQL
    print("\n=== Инициализация таблиц PostgreSQL ===")
    if not init_postgres_tables():
        print("Ошибка инициализации таблиц PostgreSQL", file=sys.stderr)
        return

    # Этап 1: Сбор данных инфляции
    print("\n=== Этап 1: Сбор данных инфляции ===")
    try:
        collect_inflation_data()
    except Exception as e:
        print(f"Критическая ошибка сбора данных: {e}", file=sys.stderr)
        return

    # Этап 2: Сбор новостей
    print("\n=== Этап 2: Сбор новостей ===")
    try:
        saved, duplicates = collect_all_news(max_news_per_source=5)
        if saved == 0:
            print("Не удалось сохранить новости", file=sys.stderr)
    except Exception as e:
        print(f"Ошибка сбора новостей: {e}", file=sys.stderr)

    # Этап 3: Нормализация данных
    print("\n=== Этап 3: Нормализация данных ===")
    try:
        if normalize_inflation_data():
            print("Данные нормализованы")
        else:
            print("Ошибка нормализации", file=sys.stderr)
    except Exception as e:
        print(f"Ошибка обработки данных: {e}", file=sys.stderr)

    # Итоговая статистика
    print("\n=== Итоги работы ===")
    display_statistics()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Критическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)