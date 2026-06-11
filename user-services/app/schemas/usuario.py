from pydantic import BaseModel, EmailStr
from typing import List, Optional


class UsuarioCriacao(BaseModel):
    nome: str
    email: EmailStr
    roles: Optional[List[str]] = None  # se não informado, usa ["PARTICIPANT"]


class UsuarioAtualizacao(BaseModel):
    nome: Optional[str] = None   # campos opcionais no PATCH
    email: Optional[EmailStr] = None


class UsuarioRoles(BaseModel):
    roles: List[str]
