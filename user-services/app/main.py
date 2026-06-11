from fastapi import FastAPI
from app.routes.usuarios import router
from app.database.database import engine
from app.models.usuario import Usuario, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FACOFFEE User Service",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def home():
    return {"mensagem": "User Service funcionando!"}
