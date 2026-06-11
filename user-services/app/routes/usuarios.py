from fastapi import APIRouter, HTTPException
from uuid import uuid4
from datetime import datetime

from app.schemas.usuario import UsuarioCriacao, UsuarioAtualizacao, UsuarioRoles

router = APIRouter(
    prefix="/users",
    tags=["Usuários"]
)

usuarios = []


@router.get("/")
def listar_usuarios():
    return usuarios


@router.post("/", status_code=201)
def criar_usuario(usuario: UsuarioCriacao):

    # Verifica e-mail duplicado
    for usuario_existente in usuarios:
        if usuario_existente["email"] == usuario.email:
            raise HTTPException(
                status_code=409,
                detail="Email já cadastrado"
            )

    # Usa os roles enviados, ou PARTICIPANT como padrão
    roles = usuario.roles if usuario.roles else ["PARTICIPANT"]

    # Valida que os roles são válidos
    roles_validos = {"MANAGER", "PARTICIPANT"}
    for role in roles:
        if role not in roles_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Role inválido: {role}. Use MANAGER ou PARTICIPANT."
            )

    novo_usuario = {
        "id": "usr_" + str(uuid4()).replace("-", "")[:12],
        "nome": usuario.nome,
        "email": usuario.email,
        "status": "ACTIVE",
        "roles": roles,
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
    dados: UsuarioAtualizacao
):

    for usuario in usuarios:
        if usuario["id"] == usuario_id:

            # Impede edição de usuário inativo
            if usuario["status"] == "INACTIVE":
                raise HTTPException(
                    status_code=409,
                    detail="Não é possível editar um usuário inativo."
                )

            # Atualiza nome se fornecido
            if dados.nome is not None:
                if len(dados.nome.strip()) < 3:
                    raise HTTPException(
                        status_code=400,
                        detail="O nome deve ter ao menos 3 caracteres."
                    )
                usuario["nome"] = dados.nome

            # Atualiza e-mail se fornecido, validando duplicata
            if dados.email is not None:
                for outro in usuarios:
                    if outro["email"] == dados.email and outro["id"] != usuario_id:
                        raise HTTPException(
                            status_code=409,
                            detail="Email já cadastrado por outro usuário."
                        )
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

            # Impede dupla desativação
            if usuario["status"] == "INACTIVE":
                raise HTTPException(
                    status_code=409,
                    detail="Usuário já está inativo."
                )

            usuario["status"] = "INACTIVE"
            usuario["deactivatedAt"] = datetime.now().isoformat()
            usuario["updatedAt"] = datetime.now().isoformat()

            return usuario

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

            # Impede alteração de roles em usuário inativo
            if usuario["status"] == "INACTIVE":
                raise HTTPException(
                    status_code=409,
                    detail="Não é possível alterar roles de um usuário inativo."
                )

            # Valida roles
            roles_validos = {"MANAGER", "PARTICIPANT"}
            for role in dados.roles:
                if role not in roles_validos:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Role inválido: {role}. Use MANAGER ou PARTICIPANT."
                    )

            usuario["roles"] = dados.roles
            usuario["updatedAt"] = datetime.now().isoformat()

            return usuario

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )
