from fastapi import FastAPI
from app.routes.usuarios import router

app = FastAPI(
    title="FACOFFEE User Service",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def home():
    return {"mensagem": "User Service funcionando!"}
