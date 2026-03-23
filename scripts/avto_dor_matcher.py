# скрипт для метчинга адресов дорог с БД Автодора 
import re, os, sys, pymorphy3
import pandas as pd
from typing import Dict
from rapidfuzz import fuzz
from fastapi import HTTPException
from functools import lru_cache

from config import ASR_NOISE, SERVICE_WORDS, THRESHOLD, PATH_TO_JSON

# Поиск модулей в директории выше
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger import logger

morph = pymorphy3.MorphAnalyzer()

def lemmatize(text: str) -> str:
    '''
    Функция lemmatize, которая лемматизирует входную фразу,
    то есть приводит ее к именительному падежу;
    
    :param text: Входной текст с различными падежными формами;
    :type text: str
    :return: Нормализованный текст;
    :rtype: str
    '''
    return " ".join(morph.parse(token)[0].normal_form 
                        for token in text.split() )

def normalize(text: str) -> str:
    '''
    Функция нормализации убирает кавычки, скобки и ряд мусорных символов,
    которые не пригодны для поиска
    
    :param text: Описание
    :type text: str
    :return: Описание
    :rtype: str
    '''
    text = text.lower()
    text = re.sub(r"[«»\"()]", " ", text)
    
    # безопасное удаление символов
    for w in ASR_NOISE + SERVICE_WORDS:
        text = re.sub(re.escape(w), " ", text)

    text = text.replace("–", "-").replace("—", "-")
    # оставляем только буквы, цифры, дефисы (все остальное заменяется на пробелы)
    text = re.sub(r"[^a-zа-я0-9\- ]", " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text

# используем кеширование, сохраняя только один вызов функции в памяти
# (по умолчанию используется 128 запоминаний вызовов функций с разными входными параметрами)
@lru_cache(maxsize=1)
def load_addresses(path: str):
    '''
    Функция для считывания дорожной карты из Json файла
    
    :param path: Путь до файла;
    :type path: str
    '''
    
    # Преобразуем в DataFrame с указанием ориентации index
    df = pd.read_json(path, orient='index')
    
    # Проверяем наличие необходимых столбцов
    if not {'original', 'normalized'}.issubset(df.columns):
        raise ValueError("JSON файл должен содержать поля 'original' и 'normalized'")
    
    return df[['original', 'normalized']]


def score(a: str, b: str) -> int:
    '''
    Функция score выдает процент, на сколько строки схожи друг с другом.
    Использует модификацию алгоритма Левенштейна из библиотеки rapidfuzz.
    
    :param a: Нормализованная фраза абонента
    :type a: str
    :param b: Нормализованный адрес из базы
    :type b: str
    :return: Значение параметра совпадения между строчками(100 - полное совпадение)
    :rtype: int
    '''
    return max(
        fuzz.token_set_ratio(a, b),
        fuzz.token_sort_ratio(a, b),
        fuzz.partial_ratio(a, b)
    )


def find_best_match(query: str, df, threshold: str = '75') -> Dict:
    '''
    Функция find_best_match проходится по всему Датафрейму
    и находит лучшее сопоставление строки абонента и строки из списка.
    
    :param query: Нормализованная строка от абонента;
    :type query: str
    :param df: Датафрейм, c валидными адресами;
    :param threshold: Граничный параметр;
    :type threshold: int
    '''
    res = False
    best_score = -1
    best_row = None

    # пробегаем по всему списку DataFrame и выдаем лучшее совпадение
    for row in df.itertuples(index=False):
        s = score(query, row.normalized)
        if s > best_score:
            best_score = s
            best_row = row
    
    if best_score > int(threshold):
        res = True

    # минимальное совпадение по best_row всегда будет найдено
    return {
        "result": str(res),
        "address": str(best_row.original),
        "score": str(round(best_score, 2))
    }

def process_address(input_string: str) -> dict:
    '''
    Функция process_address реаизует общую логику обработки адреса МосАвтоДор
    
    :param input_string: 
    :type input_string: str
    :return: 
    :rtype: dict
    '''
    logger.info(f"На вход МосАвтоДор получена следующая строка: {input_string}")
    
    try:
        norm_addres = normalize(lemmatize(input_string))
        logger.info(f"Строка после нормализации: {norm_addres}")
        
        df_norm = load_addresses(PATH_TO_JSON)
        dict_res = find_best_match(norm_addres, df_norm, THRESHOLD)
        logger.info(f"Результат работы метчера: {dict_res}")

        return dict_res

    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")