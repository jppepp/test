from bs4 import BeautifulSoup
import sys

def parse_inflation_data(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        inflation_element = soup.find('span', {'id': 'lbl_inflation_average'})
        if inflation_element:
            inflation_rate = inflation_element.text.strip().replace('%', '').strip()
            try:
                inflation_rate = float(inflation_rate)
                return inflation_rate
            except ValueError:
                print(f"Некорректное значение инфляции: {inflation_rate}", file=sys.stderr)
                return None
        else:
            print("Не удалось найти данные о годовой инфляции.", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Неожиданная ошибка при парсинге данных: {e}", file=sys.stderr)
        return None