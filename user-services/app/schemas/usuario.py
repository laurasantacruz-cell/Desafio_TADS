from pydantic import BaseModel, EmailStr


class UsuarioCriacao(BaseModel):
    nome: str
    email: EmailStr


class UsuarioRoles(BaseModel):
    roles: list[str]
