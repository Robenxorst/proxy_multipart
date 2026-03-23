import os

ASR_NOISE = [
    r"\bэ\b", r"\bну\b", r"\bвот\b", r"\bэто\b",
    r"\bтам\b", r"\bкороче\b", r"\bя\b", r"\bу\b"
]

SERVICE_WORDS = [
    r"\bул\.?\b", r"\bулица\b",
    r"\bпр-кт\b", r"\bпроспект\b",
    r"\bпункт\b", r"\bрайон\b",
    r"\bг\.?\b", r"\bгород\b",
    r"\bд\.?\b", r"\bдеревня\b",
    r"\bсело\b", r"\bпоселок\b",
    r"\bдорога\b", r"\bтрасса\b",
    r"\bшоссе\b", r"\bот\b",
    r"\bдо\b", r"\bна\b", r"\bпо\b",
    r"\bмежду\b", r"\bрядом\b",
    r"\bоколо\b", r"\bвозле\b",
    r"\bнаходиться\b", r"\bнаходится\b"
]

PATH_TO_JSON = 'maps/road_map.json'

TARGET_URL = os.getenv("TARGET_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
URL_BTI=os.getenv("URL_BTI")
AUTH_BTI=os.getenv("AUTH_BTI")
THRESHOLD=os.getenv("THRESHOLD")

if not TARGET_URL or not AUTH_TOKEN or not URL_BTI or not AUTH_BTI:
    raise RuntimeError("Не заданы базовые переменные окружения")