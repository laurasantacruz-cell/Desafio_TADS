from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from uuid import uuid4
from app.database.database import Base


def gerar_id():
    return "usr_" + uuid4().hex[:12]


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True, default=gerar_id)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, default="ACTIVE", nullable=False)
    # salvo como "MANAGER,PARTICIPANT"
    roles = Column(String, default="PARTICIPANT", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    deactivated_at = Column(DateTime(timezone=True), nullable=True)
