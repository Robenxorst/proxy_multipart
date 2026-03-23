from fastapi import HTTPException
import os, sys, httpx

# Поиск модулей в директории выше
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import TARGET_URL, AUTH_TOKEN
from logger import logger

async def fetch_4me_data(user_id: int) -> dict:
    """
    Выполняет асинхронный POST-запрос к API 4me.
    Возвращает JSON-ответ, если запрос успешен.
    """
    form_data = {
        "filter": (None, f"r.id = {user_id}")
    }

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(TARGET_URL, headers=headers, files=form_data)
            logger.info(f"Запрос к 4me завершен: статус {response.status_code}")

            # Проверяем статус ответа
            response.raise_for_status()

            # Возвращаем JSON-данные
            return response.json()

    except httpx.RequestError as e:
        logger.error(f"Ошибка подключения к 4me: {e}")
        raise HTTPException(status_code=502, detail="Ошибка соединения с 4me")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка при обращении к 4me: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail="Ошибка от 4me API")