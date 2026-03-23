import json, re, sys, os
from fastapi import HTTPException


# Поиск модулей в директории выше
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logger import logger

def company_parser(json_response: dict) -> dict:
    requests_list = json_response.get("requests", [])
    if not requests_list:
        raise HTTPException(status_code=400, detail="Некорректный ответ 4me")
    
    req = requests_list[0]
    company_name = req.get("company")

    # Если название отсутствует, то берем его из custom_fields
    if not company_name:
        custom_fields_raw = req.get("custom_fields_json")
        if not custom_fields_raw:
            raise HTTPException(status_code=400, detail="Отсутствует поле custom_fields_json")
        
        try:
            custom_fields_json = json.loads(custom_fields_raw)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга custom_fields_json: {e}")
            raise HTTPException(status_code=400, detail="Некорректный JSON в custom_fields_json")
        
        for item in custom_fields_json:
            if item["id"] == 'company_name':
                company_name = item["value"]
                break

    # Убираем мусор из названия компании
    if company_name:
        company_name = re.sub(r'["\'\\/]', '', company_name).strip()

    # Добавляем обработанный company_name в json для отправки
    req["company"] = company_name

    return json_response