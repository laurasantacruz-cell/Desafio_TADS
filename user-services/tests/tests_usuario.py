from fastapi.testclient import TestClient
from app.main import app
import base64
import json

client = TestClient(app)


def fazer_token(roles):
    header = base64.urlsafe_b64encode(json.dumps(
        {"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps(
        {"sub": "user-test-001", "email": "test@email.com", "roles": roles}).encode()).decode().rstrip("=")
    return f"Bearer {header}.{payload}.assinatura-fake"


MANAGER = fazer_token(["MANAGER"])
PARTICIPANT = fazer_token(["PARTICIPANT"])


def criar(nome="Joao Silva", email="joao@email.com", roles=None):
    body = {"nome": nome, "email": email}
    if roles:
        body["roles"] = roles
    return client.post("/users/", json=body)


def test_listar_usuarios_manager():
    res = client.get("/users/", headers={"authorization": MANAGER})
    assert res.status_code == 200


def test_listar_usuarios_sem_token():
    res = client.get("/users/")
    assert res.status_code == 401


def test_listar_usuarios_participant_negado():
    res = client.get("/users/", headers={"authorization": PARTICIPANT})
    assert res.status_code == 403


def test_criar_usuario_sucesso():
    res = criar("Maria Silva", "maria_teste@email.com")
    assert res.status_code == 201
    assert res.json()["status"] == "ACTIVE"
    assert res.json()["roles"] == ["PARTICIPANT"]


def test_criar_usuario_role_manager():
    res = criar("Chef Boss", "boss_teste@email.com", roles=["MANAGER"])
    assert res.status_code == 201
    assert res.json()["roles"] == ["MANAGER"]


def test_criar_usuario_email_duplicado():
    criar("Ana Costa", "ana_teste@email.com")
    res = criar("Ana Costa 2", "ana_teste@email.com")
    assert res.status_code == 409


def test_criar_usuario_role_invalido():
    res = criar("Teste Role", "role_teste@email.com", roles=["ADMIN"])
    assert res.status_code == 400


def test_buscar_usuario_existente():
    criado = criar("Pedro Alves", "pedro_teste@email.com").json()
    uid = criado["id"]
    res = client.get("/users/" + uid, headers={"authorization": MANAGER})
    assert res.status_code == 200


def test_buscar_usuario_inexistente():
    res = client.get("/users/usr_inexistente",
                     headers={"authorization": MANAGER})
    assert res.status_code == 404


def test_atualizar_nome():
    criado = criar("Lucas Mendes", "lucas_teste@email.com").json()
    uid = criado["id"]
    res = client.patch(
        "/users/" + uid, json={"nome": "Lucas Novo"}, headers={"authorization": MANAGER})
    assert res.status_code == 200
    assert res.json()["nome"] == "Lucas Novo"


def test_atualizar_email_duplicado():
    criar("User A", "usera_teste@email.com")
    criado_b = criar("User B", "userb_teste@email.com").json()
    uid = criado_b["id"]
    res = client.patch(
        "/users/" + uid, json={"email": "usera_teste@email.com"}, headers={"authorization": MANAGER})
    assert res.status_code == 409


def test_atualizar_usuario_inativo():
    criado = criar("Inativo Edit", "inativo_edit_teste@email.com").json()
    uid = criado["id"]
    client.delete("/users/" + uid, headers={"authorization": MANAGER})
    res = client.patch(
        "/users/" + uid, json={"nome": "Novo Nome"}, headers={"authorization": MANAGER})
    assert res.status_code == 409


def test_atualizar_nome_curto():
    criado = criar("Nome Valido", "nomeval_teste@email.com").json()
    uid = criado["id"]
    res = client.patch(
        "/users/" + uid, json={"nome": "AB"}, headers={"authorization": MANAGER})
    assert res.status_code == 400


def test_desativar_usuario():
    criado = criar("Deletar User", "deletar_teste@email.com").json()
    uid = criado["id"]
    res = client.delete("/users/" + uid, headers={"authorization": MANAGER})
    assert res.status_code == 200
    assert res.json()["status"] == "INACTIVE"


def test_desativar_usuario_ja_inativo():
    criado = criar("Duplo Delete", "duplo_teste@email.com").json()
    uid = criado["id"]
    client.delete("/users/" + uid, headers={"authorization": MANAGER})
    res = client.delete("/users/" + uid, headers={"authorization": MANAGER})
    assert res.status_code == 409


def test_desativar_usuario_inexistente():
    res = client.delete("/users/usr_naoexiste",
                        headers={"authorization": MANAGER})
    assert res.status_code == 404


def test_alterar_roles_sucesso():
    criado = criar("Role Changer", "rolechanger_teste@email.com").json()
    uid = criado["id"]
    res = client.put("/users/" + uid + "/roles",
                     json={"roles": ["MANAGER"]}, headers={"authorization": MANAGER})
    assert res.status_code == 200
    assert res.json()["roles"] == ["MANAGER"]


def test_alterar_roles_usuario_inativo():
    criado = criar("Inativo Roles", "inativo_roles_teste@email.com").json()
    uid = criado["id"]
    client.delete("/users/" + uid, headers={"authorization": MANAGER})
    res = client.put("/users/" + uid + "/roles",
                     json={"roles": ["MANAGER"]}, headers={"authorization": MANAGER})
    assert res.status_code == 409


def test_alterar_roles_invalido():
    criado = criar("Role Invalido", "role_invalido_teste@email.com").json()
    uid = criado["id"]
    res = client.put("/users/" + uid + "/roles",
                     json={"roles": ["SUPERADMIN"]}, headers={"authorization": MANAGER})
    assert res.status_code == 400


def test_alterar_roles_inexistente():
    res = client.put("/users/usr_naoexiste/roles",
                     json={"roles": ["PARTICIPANT"]}, headers={"authorization": MANAGER})
    assert res.status_code == 404


def test_alterar_roles_participant_negado():
    criado = criar("Sem Permissao", "sempermissao_teste@email.com").json()
    uid = criado["id"]
    res = client.put("/users/" + uid + "/roles",
                     json={"roles": ["MANAGER"]}, headers={"authorization": PARTICIPANT})
    assert res.status_code == 403
