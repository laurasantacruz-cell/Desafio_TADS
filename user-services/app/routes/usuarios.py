from fastapi import APIRouter, HTTPException
from uuid import uuid4
from datetime import datetime

from app.schemas.usuario import UsuarioCriacao, UsuarioRoles

router = APIRouter(
    prefix="/users",
    tags=["Usuários"]
)

usuarios = []


@router.get("/")
def listar_usuarios():
    return usuarios


@router.post("/")
def criar_usuario(usuario: UsuarioCriacao):

    # Verifica e-mail duplicado
    for usuario_existente in usuarios:
        if usuario_existente["email"] == usuario.email:
            raise HTTPException(
                status_code=409,
                detail="Email já cadastrado"
            )

    novo_usuario = {
        "id": str(uuid4()),
        "nome": usuario.nome,
        "email": usuario.email,
        "status": "ACTIVE",
        "roles": ["PARTICIPANT"],
        "createdAt": datetime.now().isoformat(),
        "updatedAt": None,
        "deactivatedAt": None
    }

    usuarios.append(novo_usuario)

    return novo_usuario


@router.get("/{usuario_id}")
def buscar_usuario(usuario_id: str):

    for usuario in usuarios:
        if usuario["id"] == usuario_id:
            return usuario

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )


@router.patch("/{usuario_id}")
def atualizar_usuario(
    usuario_id: str,
    dados: UsuarioCriacao
):

    for usuario in usuarios:
        if usuario["id"] == usuario_id:

            usuario["nome"] = dados.nome
            usuario["email"] = dados.email
            usuario["updatedAt"] = datetime.now().isoformat()

            return usuario

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )


@router.delete("/{usuario_id}")
def desativar_usuario(usuario_id: str):

    for usuario in usuarios:
        if usuario["id"] == usuario_id:

            usuario["status"] = "INACTIVE"
            usuario["deactivatedAt"] = datetime.now().isoformat()

            return {
                "mensagem": "Usuário desativado",
                "usuario": usuario
            }

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )


@router.put("/{usuario_id}/roles")
def alterar_roles(
    usuario_id: str,
    dados: UsuarioRoles
):

    for usuario in usuarios:

        if usuario["id"] == usuario_id:

            usuario["roles"] = dados.roles
            usuario["updatedAt"] = datetime.now().isoformat()

            return usuario

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )
