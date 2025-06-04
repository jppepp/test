from bs4 import BeautifulSoup
import sys
import math


def parse_inflation_data(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        inflation_element = soup.find('span', {'id': 'lbl_inflation_average'})
        if inflation_element:
            inflation_rate = inflation_element.text.strip().replace('%', '').strip()

            # Handle special cases
            if inflation_rate.lower() in ['∞', 'inf', 'nan']:
                print(f"Обнаружено некорректное значение инфляции: {inflation_rate}. Записываем 0.", file=sys.stderr)
                return 0.0

            try:
                inflation_rate = float(inflation_rate)
                if math.isnan(inflation_rate) or math.isinf(inflation_rate):
                    print(f"Обнаружено некорректное числовое значение инфляции: {inflation_rate}. Записываем 0.",
                          file=sys.stderr)
                    return 0.0
                return inflation_rate
            except ValueError:
                print(f"Некорректное значение инфляции: {inflation_rate}. Записываем 0.", file=sys.stderr)
                return 0.0
        else:
            print("Не удалось найти данные о годовой инфляции. Записываем 0.", file=sys.stderr)
            return 0.0
    except Exception as e:
        print(f"Неожиданная ошибка при парсинге данных: {e}. Записываем 0.", file=sys.stderr)
        return 0.0