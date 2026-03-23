from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
import httpx, sys, os

# Поиск модулей в директории выше
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# импорт кастомных модулей
from schemas.proxy_schema import RequestBody, BodyAutoDor
from scripts.company_parser import company_parser
from scripts.request_4me import fetch_4me_data
from scripts.mos_gor_bti import get_data_for_BTI, translate_keys, key_map
from scripts.avto_dor_matcher import process_address
from logger import logger

router = APIRouter()

@router.post("/proxy")
async def proxy(request_body: RequestBody) -> JSONResponse:
    user_id = request_body.user_id
    logger.info(f"Получен user_id: {user_id}")

    try:
        response_4me = await fetch_4me_data(user_id)

        new_json = company_parser(response_4me)
        logger.info(f"Данные {user_id} успешно обработаны!")

        return JSONResponse(content=new_json, status_code=200)

    except httpx.RequestError as e:
        logger.error(f"Ошибка запроса к 4me: {e}")
        raise HTTPException(status_code=502, detail="Ошибка при запросе к 4me")

    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
    
@router.get("/mos_gor_bti")
async def proxy_bti(phone_number: str = Query(..., min_length=10, max_length=10)) -> JSONResponse:
    if not phone_number.isdigit():
        raise HTTPException(status_code=400, detail="Номер телефона должен содержать только цифры")
    
    logger.info(f"Получен номер телефона: {phone_number}")

    try:
        # Выполняем запрос по номеру телефона
        json_bti = await get_data_for_BTI(phone_number)

        new_json_bti = translate_keys(json_bti, key_map)
        logger.info(f"Данные номера {phone_number} успешно обработаны!")

        return JSONResponse(content=new_json_bti, status_code=200)

    except httpx.RequestError as e:
        logger.error(f"Ошибка запроса к БТИ: {e}")
        raise HTTPException(status_code=502, detail="Ошибка при запросе к БТИ")

    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
    
@router.post("/mos_avto_dor")
async def mos_avto_dor(input_body: BodyAutoDor) -> JSONResponse:
    try:
        # вынос синхронной логики в threadpool
        dict_res = await run_in_threadpool(process_address, input_body.address)

        return JSONResponse(content=dict_res, status_code=200)

    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")