from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
from postgres_init import init_postgres_tables
from save_to_db import save_to_postgres
from fastapi.openapi.utils import get_openapi
import yaml
from fastapi.responses import PlainTextResponse
import sys

app = FastAPI(
    title="Inflation Data API",
    description="API для сбора и хранения данных об инфляции",
    version="1.0.0",
    openapi_version="3.0.2",
)

class InflationData(BaseModel):
    country: str
    year: int
    inflation_rate: float
    data_type: str = "CPI Inflation (API)"
    source: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    if not init_postgres_tables():
        raise RuntimeError("Не удалось инициализировать таблицы PostgreSQL")

@app.post("/api/inflation/", summary="Сохранить данные об инфляции", response_model=InflationData)
async def save_inflation_data(data: InflationData):
    try:
        save_to_postgres(
            rate=data.inflation_rate,
            year=data.year,
            country=data.country,
            data_type=data.data_type,
            source=data.source
        )
        return data
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/inflation/", summary="Получить данные об инфляции")
async def fetch_inflation_data(country: str, year: int):
    api_url = f"https://api.example.com/inflation?country={country}&year={year}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {"inflation_rate": data.get('inflation_rate')}
        else:
            raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе к API")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Тайм-аут при запросе к API")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе к API: {e}")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["openapi"] = "3.0.2"

    for schema in openapi_schema["components"]["schemas"].values():
        for prop in schema.get("properties", {}).values():
            if "anyOf" in prop:
                if any(t.get("type") == "null" for t in prop["anyOf"]):
                    types = [t for t in prop["anyOf"] if t.get("type") != "null"]
                    if types:
                        prop.update(types[0])
                        prop["nullable"] = True
                    del prop["anyOf"]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/openapi.yaml", response_class=PlainTextResponse, include_in_schema=False)
async def get_openapi_yaml():
    return yaml.dump(app.openapi(), sort_keys=False)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)