import requests
import sys

def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Ошибка при запросе к {url}: {response.status_code}", file=sys.stderr)
            return None
    except requests.exceptions.Timeout:
        print(f"Тайм-аут при запросе к {url}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к {url}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при запросе к {url}: {e}", file=sys.stderr)
        return None