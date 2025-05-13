import requests
import sys
from save_to_db import save_to_postgres

def fetch_inflation_data_from_api(country, year):
    api_url = f"https://api.example.com/inflation?country={country}&year={year}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('inflation_rate')
        else:
            print(f"Ошибка при запросе к API для {country} за {year} год: {response.status_code}", file=sys.stderr)
            return None
    except requests.exceptions.Timeout:
        print(f"Тайм-аут при запросе к API для {country} за {year} год", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API для {country} за {year} год: {e}", file=sys.stderr)
        return None

def save_inflation_data_from_api(countries, years):
    try:
        for country in countries:
            for year in years:
                inflation_rate = fetch_inflation_data_from_api(country, year)
                if inflation_rate is not None:
                    print(f"Годовая инфляция в {country} за {year} год (API): {inflation_rate}%")
                    try:
                        save_to_postgres(
                            rate=inflation_rate,
                            year=year,
                            country=country,
                            data_type='CPI Inflation (API)'
                        )
                    except Exception:
                        print(f"Не удалось сохранить данные для {country} за {year} год", file=sys.stderr)
                else:
                    print(f"Не удалось получить данные об инфляции для {country} за {year} год через API.", file=sys.stderr)
    except Exception as e:
        print(f"Неожиданная ошибка при сохранении данных из API: {e}", file=sys.stderr)
        raise