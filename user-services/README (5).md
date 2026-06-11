# FACOFFEE — Users Service

Serviço responsável pelo gerenciamento de usuários da aplicação FACOFFEE.

## Tecnologias

- Python 3.13+
- FastAPI
- Pydantic
- SQLAlchemy + SQLite

## Pré-requisitos

- Python instalado
- Docker e Docker Compose (para subir a infraestrutura)

## Instalação e execução

### 1. Entre na pasta do serviço

```bash
cd user-services
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install fastapi uvicorn pydantic[email] sqlalchemy pytest httpx
```

### 4. Suba a infraestrutura (na raiz do projeto FACOFFEE)

```bash
docker compose up -d
```

### 5. Inicie o serviço

```bash
uvicorn app.main:app --reload --port 8001
```

A API estará disponível em: http://localhost:8001

Documentação interativa: http://localhost:8001/docs

---

## Endpoints

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|--------------|
| POST | `/users/` | Criar usuário | Pública |
| GET | `/users/` | Listar usuários | MANAGER |
| GET | `/users/{id}` | Buscar por ID | Autenticado |
| PATCH | `/users/{id}` | Atualizar dados | Autenticado |
| DELETE | `/users/{id}` | Desativar usuário | Autenticado |
| PUT | `/users/{id}/roles` | Alterar roles | MANAGER |

---

## Regras de negócio

- E-mail deve ser único
- Usuário criado inicia com status `ACTIVE` e role `PARTICIPANT`
- Usuário inativo não pode ser editado, desativado novamente ou ter roles alterados
- Apenas `MANAGER` pode listar todos os usuários e alterar roles
- Roles válidos: `MANAGER`, `PARTICIPANT`

---

## Executando os testes

```bash
pytest tests/tests_usuario.py -v
```

---

## Estrutura do projeto

```
user-services/
├── app/
│   ├── database/
│   │   └── database.py      # Configuração do banco de dados SQLite
│   ├── models/
│   │   └── usuario.py       # Model SQLAlchemy
│   ├── routes/
│   │   └── usuarios.py      # Endpoints do serviço
│   ├── schemas/
│   │   └── usuario.py       # Schemas Pydantic (validação de dados)
│   └── main.py              # Inicialização da aplicação FastAPI
├── tests/
│   └── tests_usuario.py     # Testes automatizados (19 testes)
└── README.md
```