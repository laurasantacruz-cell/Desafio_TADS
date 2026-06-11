from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.schemas.usuario import UsuarioCriacao, UsuarioAtualizacao, UsuarioRoles
from app.database.database import get_db
from app.models.usuario import Usuario
from app.auth import get_current_user, require_manager

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

ROLES_VALIDOS = {"MANAGER", "PARTICIPANT"}


def usuario_para_dict(u: Usuario) -> dict:
    return {
        "id": u.id,
        "nome": u.nome,
        "email": u.email,
        "status": u.status,
        "roles": u.roles.split(","),
        "createdAt": u.created_at.isoformat() if u.created_at else None,
        "updatedAt": u.updated_at.isoformat() if u.updated_at else None,
        "deactivatedAt": u.deactivated_at.isoformat() if u.deactivated_at else None,
    }


# POST /users — publico, sem autenticacao
@router.post("/", status_code=201)
def criar_usuario(usuario: UsuarioCriacao, db: Session = Depends(get_db)):

    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(status_code=409, detail="Email ja cadastrado")

    roles = usuario.roles if usuario.roles else ["PARTICIPANT"]

    for role in roles:
        if role not in ROLES_VALIDOS:
            raise HTTPException(
                status_code=400, detail=f"Role invalido: {role}. Use MANAGER ou PARTICIPANT.")

    novo = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        status="ACTIVE",
        roles=",".join(roles),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return usuario_para_dict(novo)


# GET /users — somente MANAGER
@router.get("/")
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    require_manager(current_user)
    usuarios = db.query(Usuario).all()
    return [usuario_para_dict(u) for u in usuarios]


# GET /users/{id} — qualquer usuario autenticado
@router.get("/{usuario_id}")
def buscar_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return usuario_para_dict(usuario)


# PATCH /users/{id} — usuario autenticado (si mesmo ou MANAGER)
@router.patch("/{usuario_id}")
def atualizar_usuario(
    usuario_id: str,
    dados: UsuarioAtualizacao,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    if usuario.status == "INACTIVE":
        raise HTTPException(
            status_code=409, detail="Nao e possivel editar um usuario inativo.")

    if dados.nome is not None:
        if len(dados.nome.strip()) < 3:
            raise HTTPException(
                status_code=400, detail="O nome deve ter ao menos 3 caracteres.")
        usuario.nome = dados.nome

    if dados.email is not None:
        duplicado = db.query(Usuario).filter(
            Usuario.email == dados.email, Usuario.id != usuario_id).first()
        if duplicado:
            raise HTTPException(
                status_code=409, detail="Email ja cadastrado por outro usuario.")
        usuario.email = dados.email

    usuario.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(usuario)
    return usuario_para_dict(usuario)


# DELETE /users/{id} — usuario autenticado
@router.delete("/{usuario_id}")
def desativar_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    if usuario.status == "INACTIVE":
        raise HTTPException(status_code=409, detail="Usuario ja esta inativo.")

    now = datetime.now(timezone.utc)
    usuario.status = "INACTIVE"
    usuario.deactivated_at = now
    usuario.updated_at = now
    db.commit()
    db.refresh(usuario)
    return usuario_para_dict(usuario)


# PUT /users/{id}/roles — somente MANAGER
@router.put("/{usuario_id}/roles")
def alterar_roles(
    usuario_id: str,
    dados: UsuarioRoles,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    require_manager(current_user)

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    if usuario.status == "INACTIVE":
        raise HTTPException(
            status_code=409, detail="Nao e possivel alterar roles de um usuario inativo.")

    for role in dados.roles:
        if role not in ROLES_VALIDOS:
            raise HTTPException(
                status_code=400, detail=f"Role invalido: {role}. Use MANAGER ou PARTICIPANT.")

    usuario.roles = ",".join(dados.roles)
    usuario.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(usuario)
    return usuario_para_dict(usuario)
