import requests
from bs4 import BeautifulSoup
import urllib3
from typing import List, Dict, Tuple
from datetime import datetime
import sys
from postgres_init_news import PostgresNewsManager

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NewsParser:
    """Базовый класс для парсеров новостей"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def parse_news(self, max_news: int = 5) -> List[Dict]:
        """Основной метод для парсинга новостей"""
        raise NotImplementedError


class MinfinParser(NewsParser):
    """Парсер новостей Минфина России"""

    def parse_news(self, max_news: int = 5) -> List[Dict]:
        url = "https://minfin.gov.ru/ru/press-center/"
        news_list = []

        try:
            response = self.session.get(url, verify=False, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            news_cards = soup.find_all('div', class_='news_card_min')[:max_news]

            for card in news_cards:
                try:
                    news_item = {
                        'title': self._parse_title(card),
                        'date': self._parse_date(card),
                        'link': self._parse_link(card),
                        'source': 'MinFin Russia'
                    }
                    news_list.append(news_item)
                except Exception as e:
                    print(f"Ошибка обработки новости Минфина: {e}", file=sys.stderr)

            return news_list

        except Exception as e:
            print(f"Ошибка парсинга Минфина: {e}", file=sys.stderr)
            return []

    def _parse_title(self, card) -> str:
        title_tag = card.find('a', class_='news_title')
        return title_tag.get_text(strip=True) if title_tag else "Нет заголовка"

    def _parse_date(self, card) -> str:
        date_tag = card.find('span', class_='news_date')
        return date_tag.get_text(strip=True) if date_tag else "Нет даты"

    def _parse_link(self, card) -> str:
        link_tag = card.find('a', class_='news_title')
        relative_link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "#"
        return f"https://minfin.gov.ru{relative_link}" if relative_link.startswith('/') else relative_link


class EconomyParser(NewsParser):
    """Парсер новостей Минэкономразвития России"""

    def parse_news(self, max_news: int = 5) -> List[Dict]:
        url = "https://www.economy.gov.ru/material/news/"
        news_list = []

        try:
            response = self.session.get(url, verify=False, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.select('article.e-news__item')[:max_news]

            for item in news_items:
                try:
                    news_item = {
                        'title': self._parse_title(item),
                        'date': self._parse_date(item),
                        'link': self._parse_link(item),
                        'source': 'MinEconomy Russia'
                    }
                    news_list.append(news_item)
                except Exception as e:
                    print(f"Ошибка обработки новости Минэкономразвития: {e}", file=sys.stderr)

            return news_list

        except Exception as e:
            print(f"Ошибка парсинга Минэкономразвития: {e}", file=sys.stderr)
            return []

    def _parse_title(self, item) -> str:
        title_tag = item.select_one('header.e-title a')
        return title_tag.get_text(strip=True) if title_tag else "Нет заголовка"

    def _parse_date(self, item) -> str:
        date_tag = item.select_one('div.e-date')
        if date_tag:
            date_text = date_tag.get_text(strip=True)
            return date_text[:10] if len(date_text) >= 10 else "Нет даты"
        return "Нет даты"

    def _parse_link(self, item) -> str:
        title_tag = item.select_one('header.e-title a')
        if title_tag and 'href' in title_tag.attrs:
            link = title_tag['href']
            return f"https://www.economy.gov.ru{link}" if link.startswith('/') else link
        return "#"


class WorldBankParser(NewsParser):
    """Парсер новостей World Bank"""

    def parse_news(self, max_news: int = 5) -> List[Dict]:
        url = "https://www.worldbank.org/en/news"
        news_list = []

        try:
            response = self.session.get(url, verify=False, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            news_cards = soup.find_all('div', class_='lp__primary_card')[:max_news]

            for card in news_cards:
                try:
                    news_item = {
                        'title': self._parse_title(card),
                        'date': self._parse_date(card),
                        'link': self._parse_link(card),
                        'source': 'World Bank'
                    }
                    news_list.append(news_item)
                except Exception as e:
                    print(f"Ошибка обработки новости World Bank: {e}", file=sys.stderr)

            return news_list

        except Exception as e:
            print(f"Ошибка парсинга World Bank: {e}", file=sys.stderr)
            return []

    def _parse_title(self, card) -> str:
        title_tag = card.find('div', class_='lp__card_title').find('a')
        return title_tag.get_text(strip=True) if title_tag else "No title"

    def _parse_date(self, card) -> str:
        date_tag = card.find('div', class_='lp__hammer').find('span')
        return date_tag.get_text(strip=True) if date_tag else "No date"

    def _parse_link(self, card) -> str:
        title_tag = card.find('div', class_='lp__card_title').find('a')
        link = title_tag['href'] if title_tag and 'href' in title_tag.attrs else "#"
        return link if link.startswith('http') else f"https://www.worldbank.org{link}"


def collect_all_news(max_news_per_source: int = 5) -> Tuple[int, int]:
    """Собирает новости со всех источников и сохраняет в БД"""
    parsers = {
        'MinFin': MinfinParser(),
        'MinEconomy': EconomyParser(),
        'WorldBank': WorldBankParser()
    }

    all_news = []
    for source_name, parser in parsers.items():
        try:
            news = parser.parse_news(max_news_per_source)
            all_news.extend(news)
            print(f"Получено {len(news)} новостей от {source_name}")
        except Exception as e:
            print(f"Ошибка при парсинге {source_name}: {e}", file=sys.stderr)

    if not all_news:
        print("Не удалось получить новости ни с одного источника", file=sys.stderr)
        return (0, 0)

    manager = PostgresNewsManager()
    try:
        if not manager.connect():
            print("Ошибка подключения к БД", file=sys.stderr)
            return (0, 0)

        saved, duplicates = manager.save_news_batch(all_news)
        print(f"Сохранено новостей: {saved} (дубликатов: {duplicates})")
        return (saved, duplicates)

    except Exception as e:
        print(f"Ошибка сохранения новостей: {e}", file=sys.stderr)
        return (0, 0)
    finally:
        manager.close()