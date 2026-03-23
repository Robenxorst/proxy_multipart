import uvicorn

if __name__ == "__main__":
    # запуск сервера uvicorn на порту 8091
    uvicorn.run("main:app", host="0.0.0.0", port=8091)