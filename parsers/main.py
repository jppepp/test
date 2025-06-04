import sys
import logging
from typing import Dict, List
from datetime import datetime
from database_creator import create_database
from postgres_init_news import PostgresNewsManager
from get_html import get_html
from parsers import (
    parse_ppi_data,
    parse_cpi_housing_utilities,
    parse_cpi_transportation,
    parse_food_inflation
)
from parse_inflation_data import parse_inflation_data
from save_to_db import save_to_postgres
from normalization import normalize_inflation_data
from news_parser import collect_all_news


class EconomicDataMonitor:
    """Основной класс системы мониторинга экономических данных"""

    def __init__(self):
        self.logger = self._setup_logger()
        self.news_manager = PostgresNewsManager()
        self.countries = ['Brazil', 'China', 'Russia', 'Indonesia', 'India']
        self.years = list(range(2015, 2026))
        self.data_sources = {
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

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """Настройка системы логирования"""
        logger = logging.getLogger('economic_monitor')
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Логирование в файл
        file_handler = logging.FileHandler('economic_monitor.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Логирование в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def _initialize_database(self) -> bool:
        """Инициализация базы данных"""
        try:
            self.logger.info("Инициализация базы данных...")
            create_database()
            self.logger.info("База данных успешно инициализирована")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации БД: {e}", exc_info=True)
            return False

    def collect_inflation_data(self) -> None:
        """Сбор данных по инфляции"""
        self.logger.info("Начало сбора данных по инфляции")

        for country in self.countries:
            self.logger.info(f"Обработка данных для {country}")

            # Обработка данных с Trading Economics
            for data_type, config in self.data_sources.items():
                try:
                    url = config['url'].format(country.lower())
                    self.logger.debug(f"Запрос данных: {url}")

                    html = get_html(url)
                    if not html:
                        self.logger.warning(f"Не удалось получить HTML для {data_type}")
                        continue

                    rate = config['parser'](html)
                    if rate is None:
                        self.logger.warning(f"Не удалось распарсить данные для {data_type}")
                        rate = 0

                    save_to_postgres(
                        rate=rate,
                        year=2025,  # Текущий год
                        country=country,
                        data_type=data_type,
                        source=config['source']
                    )
                    self.logger.info(f"{data_type}: {rate}%")

                except Exception as e:
                    self.logger.error(
                        f"Ошибка обработки {data_type} для {country}: {e}",
                        exc_info=True
                    )

            # Обработка данных с Inflation.eu
            for year in self.years:
                try:
                    url = (
                        f"https://www.inflation.eu/en/inflation-rates/"
                        f"{country.lower()}/historic-inflation/"
                        f"cpi-inflation-{country.lower()}-{year}.aspx"
                    )
                    self.logger.debug(f"Запрос данных: {url}")

                    html = get_html(url)
                    if not html:
                        self.logger.warning(f"Не удалось получить данные за {year} год")
                        continue

                    inflation_rate = parse_inflation_data(html)
                    if inflation_rate is None:
                        self.logger.warning(f"Не удалось распарсить данные за {year} год")
                        continue

                    save_to_postgres(
                        rate=inflation_rate,
                        year=year,
                        country=country,
                        data_type='CPI Inflation',
                        source='Inflation.eu'
                    )
                    self.logger.info(f"Инфляция за {year}: {inflation_rate}%")

                except Exception as e:
                    self.logger.error(
                        f"Ошибка обработки данных за {year} год: {e}",
                        exc_info=True
                    )

        self.logger.info("Завершение сбора данных по инфляции")

    def collect_news_data(self) -> None:
        """Сбор новостных данных"""
        self.logger.info("Начало сбора новостей")
        try:
            saved, duplicates = collect_all_news(max_news_per_source=5)
            self.logger.info(f"Сохранено новостей: {saved} (дубликатов: {duplicates})")
        except Exception as e:
            self.logger.error(f"Ошибка сбора новостей: {e}", exc_info=True)

    def normalize_data(self) -> None:
        """Нормализация данных"""
        self.logger.info("Начало нормализации данных")
        try:
            if normalize_inflation_data():
                self.logger.info("Данные успешно нормализованы")
            else:
                self.logger.error("Ошибка нормализации данных")
        except Exception as e:
            self.logger.error(f"Ошибка нормализации: {e}", exc_info=True)

    def display_statistics(self) -> None:
        """Отображение статистики"""
        try:
            self.logger.info("Формирование статистики")

            # Статистика новостей
            news_stats = self.news_manager.get_news_statistics()
            if news_stats:
                print("\n=== Статистика новостей ===")
                print(f"Всего новостей: {news_stats['total']}")
                print("По источникам:")
                for source, count in news_stats['by_source'].items():
                    print(f"  {source}: {count}")
                print(f"Последнее обновление: {news_stats['last_update']}")

            # Последние новости
            latest_news = self.news_manager.get_latest_news(5)
            if latest_news:
                print("\n=== Последние новости ===")
                for idx, news in enumerate(latest_news, 1):
                    print(f"\n{idx}. [{news['source']}] {news['title']}")
                    print(f"   Дата: {news['date']}")
                    print(f"   Ссылка: {news['link']}")

        except Exception as e:
            self.logger.error(f"Ошибка формирования статистики: {e}", exc_info=True)

    def run(self) -> None:
        """Основной цикл работы системы"""
        try:
            self.logger.info("=== Запуск системы мониторинга экономических данных ===")

            # Этап 1: Инициализация БД
            if not self._initialize_database():
                self.logger.error("Не удалось инициализировать БД. Завершение работы.")
                return

            # Этап 2: Сбор данных инфляции
            self.logger.info("=== Этап 1: Сбор данных инфляции ===")
            self.collect_inflation_data()

            # Этап 3: Сбор новостей
            self.logger.info("=== Этап 2: Сбор новостей ===")
            self.collect_news_data()

            # Этап 4: Нормализация данных
            self.logger.info("=== Этап 3: Нормализация данных ===")
            self.normalize_data()

            # Итоговая статистика
            self.logger.info("=== Итоги работы ===")
            self.display_statistics()

            self.logger.info("Работа системы успешно завершена")

        except Exception as e:
            self.logger.critical(f"Критическая ошибка: {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    monitor = EconomicDataMonitor()
    monitor.run()