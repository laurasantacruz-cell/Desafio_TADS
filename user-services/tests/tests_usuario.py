from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def criar(nome="Joao Silva", email="joao@email.com", roles=None):
    body = {"nome": nome, "email": email}
    if roles:
        body["roles"] = roles
    return client.post("/users/", json=body)


def test_criar_usuario_sucesso():
    res = criar("Maria Silva", "maria_teste@email.com")
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "maria_teste@email.com"
    assert data["status"] == "ACTIVE"
    assert data["roles"] == ["PARTICIPANT"]


def test_criar_usuario_role_padrao_participant():
    res = criar("Carlos Lima", "carlos_teste@email.com")
    assert res.status_code == 201
    assert res.json()["roles"] == ["PARTICIPANT"]


def test_criar_usuario_com_role_manager():
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


def test_listar_usuarios():
    res = client.get("/users/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_buscar_usuario_existente():
    criado = criar("Pedro Alves", "pedro_teste@email.com").json()
    res = client.get(f"/users/{criado['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == criado["id"]


def test_buscar_usuario_inexistente():
    res = client.get("/users/usr_inexistente")
    assert res.status_code == 404


def test_atualizar_nome():
    criado = criar("Lucas Mendes", "lucas_teste@email.com").json()
    res = client.patch(f"/users/{criado['id']}", json={"nome": "Lucas Novo"})
    assert res.status_code == 200
    assert res.json()["nome"] == "Lucas Novo"
    assert res.json()["updatedAt"] is not None


def test_atualizar_email_duplicado():
    criar("User A", "usera_teste@email.com")
    criado_b = criar("User B", "userb_teste@email.com").json()
    res = client.patch(
        f"/users/{criado_b['id']}", json={"email": "usera_teste@email.com"})
    assert res.status_code == 409


def test_atualizar_usuario_inativo():
    criado = criar("Inativo Edit", "inativo_edit_teste@email.com").json()
    client.delete(f"/users/{criado['id']}")
    res = client.patch(f"/users/{criado['id']}", json={"nome": "Novo Nome"})
    assert res.status_code == 409


def test_atualizar_nome_curto():
    criado = criar("Nome Valido", "nomeval_teste@email.com").json()
    res = client.patch(f"/users/{criado['id']}", json={"nome": "AB"})
    assert res.status_code == 400


def test_desativar_usuario():
    criado = criar("Deletar User", "deletar_teste@email.com").json()
    res = client.delete(f"/users/{criado['id']}")
    assert res.status_code == 200
    assert res.json()["status"] == "INACTIVE"
    assert res.json()["deactivatedAt"] is not None


def test_desativar_usuario_ja_inativo():
    criado = criar("Duplo Delete", "duplo_teste@email.com").json()
    client.delete(f"/users/{criado['id']}")
    res = client.delete(f"/users/{criado['id']}")
    assert res.status_code == 409


def test_desativar_usuario_inexistente():
    res = client.delete("/users/usr_naoexiste")
    assert res.status_code == 404


def test_alterar_roles_sucesso():
    criado = criar("Role Changer", "rolechanger_teste@email.com").json()
    res = client.put(
        f"/users/{criado['id']}/roles", json={"roles": ["MANAGER"]})
    assert res.status_code == 200
    assert res.json()["roles"] == ["MANAGER"]


def test_alterar_roles_usuario_inativo():
    criado = criar("Inativo Roles", "inativo_roles_teste@email.com").json()
    client.delete(f"/users/{criado['id']}")
    res = client.put(
        f"/users/{criado['id']}/roles", json={"roles": ["MANAGER"]})
    assert res.status_code == 409


def test_alterar_roles_invalido():
    criado = criar("Role Invalido", "role_invalido_teste@email.com").json()
    res = client.put(f"/users/{criado['id']}/roles",
                     json={"roles": ["SUPERADMIN"]})
    assert res.status_code == 400


def test_alterar_roles_usuario_inexistente():
    res = client.put("/users/usr_naoexiste/roles",
                     json={"roles": ["PARTICIPANT"]})
    assert res.status_code == 404
