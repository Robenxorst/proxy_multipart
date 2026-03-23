from fastapi import FastAPI
from routes.proxy_route import router

app = FastAPI(title="Proxy 4me API")
app.include_router(router)