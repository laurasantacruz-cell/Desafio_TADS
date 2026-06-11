from fastapi import Header, HTTPException
from jose import jwt, JWTError
from typing import Optional


def get_current_user(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Token ausente ou invalido.")

    token = authorization.replace("Bearer ", "")

    try:
        # O Nginx ja valida a assinatura, aqui so lemos o payload
        payload = jwt.decode(token, options={"verify_signature": False})

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token invalido.")

        # Tenta pegar roles de dois lugares possiveis no token do Keycloak
        roles = payload.get("roles", [])
        if not roles:
            roles = payload.get("realm_access", {}).get("roles", [])

        return {
            "id": user_id,
            "email": payload.get("email", ""),
            "roles": roles,
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido.")


def require_manager(current_user: dict):
    if "MANAGER" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=403,
            detail="Usuario autenticado nao possui permissao para acessar este recurso."
        )
