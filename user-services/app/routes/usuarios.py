from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.schemas.usuario import UsuarioCriacao, UsuarioAtualizacao, UsuarioRoles
from app.database.database import get_db
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/users",
    tags=["Usuários"]
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


@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return [usuario_para_dict(u) for u in usuarios]


@router.post("/", status_code=201)
def criar_usuario(usuario: UsuarioCriacao, db: Session = Depends(get_db)):

    # Verifica e-mail duplicado
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(status_code=409, detail="Email já cadastrado")

    # Roles padrão
    roles = usuario.roles if usuario.roles else ["PARTICIPANT"]

    # Valida roles
    for role in roles:
        if role not in ROLES_VALIDOS:
            raise HTTPException(
                status_code=400, detail=f"Role inválido: {role}. Use MANAGER ou PARTICIPANT.")

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


@router.get("/{usuario_id}")
def buscar_usuario(usuario_id: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_para_dict(usuario)


@router.patch("/{usuario_id}")
def atualizar_usuario(usuario_id: str, dados: UsuarioAtualizacao, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Impede edição de usuário inativo
    if usuario.status == "INACTIVE":
        raise HTTPException(
            status_code=409, detail="Não é possível editar um usuário inativo.")

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
                status_code=409, detail="Email já cadastrado por outro usuário.")
        usuario.email = dados.email

    usuario.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(usuario)
    return usuario_para_dict(usuario)


@router.delete("/{usuario_id}")
def desativar_usuario(usuario_id: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Impede dupla desativação
    if usuario.status == "INACTIVE":
        raise HTTPException(status_code=409, detail="Usuário já está inativo.")

    now = datetime.now(timezone.utc)
    usuario.status = "INACTIVE"
    usuario.deactivated_at = now
    usuario.updated_at = now
    db.commit()
    db.refresh(usuario)
    return usuario_para_dict(usuario)


@router.put("/{usuario_id}/roles")
def alterar_roles(usuario_id: str, dados: UsuarioRoles, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if usuario.status == "INACTIVE":
        raise HTTPException(
            status_code=409, detail="Não é possível alterar roles de um usuário inativo.")

    for role in dados.roles:
        if role not in ROLES_VALIDOS:
            raise HTTPException(
                status_code=400, detail=f"Role inválido: {role}. Use MANAGER ou PARTICIPANT.")

    usuario.roles = ",".join(dados.roles)
    usuario.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(usuario)
    return usuario_para_dict(usuario)
