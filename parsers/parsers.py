from bs4 import BeautifulSoup
import sys

def handle_parsing_error(parser_name, e):
    print(f"Ошибка в парсере {parser_name}: {e}", file=sys.stderr)
    return 0

def parse_ppi_data(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='table table-hover')
        if not table:
            print("Не удалось найти таблицу с данными PPI. Записываем 0.", file=sys.stderr)
            return 0

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) > 1 and "Producer Prices" in cells[0].text.strip():
                last_value = cells[1].text.strip()
                previous_value = cells[2].text.strip()
                try:
                    last_value = float(last_value)
                    previous_value = float(previous_value)
                    ppi_inflation = ((last_value - previous_value) / previous_value) * 100
                    return round(ppi_inflation, 2)
                except ValueError:
                    print(f"Некорректные значения PPI: {last_value}, {previous_value}", file=sys.stderr)
                    return 0

        print("Не удалось найти данные PPI. Записываем 0.", file=sys.stderr)
        return 0
    except Exception as e:
        return handle_parsing_error("PPI", e)

def parse_cpi_housing_utilities(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='table table-hover')
        if not table:
            print("Не удалось найти таблицу с данными CPI Housing. Записываем 0.", file=sys.stderr)
            return 0

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) > 1 and "CPI Housing Utilities" in cells[0].text.strip():
                last_value = cells[1].text.strip()
                previous_value = cells[2].text.strip()
                try:
                    last_value = float(last_value)
                    previous_value = float(previous_value)
                    cpi_inflation = ((last_value - previous_value) / previous_value) * 100
                    return round(cpi_inflation, 2)
                except ValueError:
                    print(f"Некорректные значения CPI Housing: {last_value}, {previous_value}", file=sys.stderr)
                    return 0

        print("Не удалось найти данные CPI Housing. Записываем 0.", file=sys.stderr)
        return 0
    except Exception as e:
        return handle_parsing_error("CPI Housing", e)

def parse_cpi_transportation(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='table table-hover')
        if not table:
            print("Не удалось найти таблицу с данными CPI Transportation. Записываем 0.", file=sys.stderr)
            return 0

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) > 1 and "CPI Transportation" in cells[0].text.strip():
                last_value = cells[1].text.strip()
                previous_value = cells[2].text.strip()
                try:
                    last_value = float(last_value)
                    previous_value = float(previous_value)
                    cpi_inflation = ((last_value - previous_value) / previous_value) * 100
                    return round(cpi_inflation, 2)
                except ValueError:
                    print(f"Некорректные значения CPI Transportation: {last_value}, {previous_value}", file=sys.stderr)
                    return 0

        print("Не удалось найти данные CPI Transportation. Записываем 0.", file=sys.stderr)
        return 0
    except Exception as e:
        return handle_parsing_error("CPI Transportation", e)

def parse_food_inflation(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='table table-hover')
        if not table:
            print("Не удалось найти таблицу с данными Food Inflation. Записываем 0.", file=sys.stderr)
            return 0

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) > 1 and "Food Inflation" in cells[0].text.strip():
                last_value = cells[1].text.strip()
                try:
                    return float(last_value)
                except ValueError:
                    print(f"Некорректное значение Food Inflation: {last_value}", file=sys.stderr)
                    return 0

        print("Не удалось найти данные Food Inflation. Записываем 0.", file=sys.stderr)
        return 0
    except Exception as e:
        return handle_parsing_error("Food Inflation", e)