# данный скрипт изменяет кирилицу в json заказчика на латиницу
# Для этого используется endpoint /mos_gor_bti

from fastapi import HTTPException
import os, sys, httpx

# Поиск модулей в директории выше
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import URL_BTI, AUTH_BTI
from logger import logger

from typing import Any, Dict, List, Union

# кастомный класс
JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

# карта для замены русских символов на английские
key_map = {
    "Контрагент": "Counterparty",
    "E_Mail": "Email",
    "Договоры": "Contracts",
    "Договор": "ContractNumber",
    "Дата": "Date",
    "Сумма": "Amount",
    "СчетаНаОплату": "Invoices",
    "Номер": "InvoiceNumber",
    "ПлановаяДатаОкончанияРабот": "PlannedCompletionDate",
    "ДатаВыходаНаОбъект": "SiteVisitDate",
    "Статус": "Status"
}

# ассинхронный запрос по номеру телефона
async def get_data_for_BTI(phone_number: str) -> JSONType:
    GET_BTI = f"{URL_BTI}?phone={phone_number}"

    headers = {
            "Authorization": f"Basic {AUTH_BTI}",
            "Accept": "application/json"
            }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(GET_BTI, headers=headers)
            logger.info(f"Запрос к БТИ выполнен: статус {response.status_code}")
            # проверка статуса ответа
            response.raise_for_status()
            # Возвращаем JSON-данные
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Ошибка при запосе к БТИ: {e}")
        raise HTTPException(status_code=502, detail="Ошибка соединения с 4me")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка при обращении к БТИ: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail="Ошибка от БТИ API")

def translate_keys(json: JSONType, mapping: dict) -> JSONType:
    if isinstance(json, dict):
        new_dict = {}
        for key, value in json.items():
            new_key = mapping.get(key, key)  # если ключа нет в словаре — оставляем как есть
            new_dict[new_key] = translate_keys(value, mapping) # рекурсивно обходим структуру JSON
        return new_dict

    elif isinstance(json, list):
        return [translate_keys(item, mapping) for item in json]

    else:
        return json