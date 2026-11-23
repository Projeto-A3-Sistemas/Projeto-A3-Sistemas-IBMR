"""Testes do P1 que rodam sem banco e sem Docker.
Rodar na pasta api-clinica:  python -m pytest tests/test_seguranca.py -v

Cobrem: conferência da senha, tipos de token (login x confirmacao) e a protecao das
rotas privadas (sem token -> 401). Os fluxos com banco (login, logout,
microchip, envio ao governo) estao no teste ponta a ponta em tests/integracao/.
"""
import bcrypt
import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import JWT_SECRET
from app.core.security import (
    JWT_ALGORITHM,
    TIPO_TOKEN_ACESSO,
    criar_token_acesso,
    criar_token_confirmacao,
    validar_token_confirmacao,
    verificar_senha,
)
from app.main import app

# Sem "with": nao roda o lifespan, entao o reenvio automatico nao liga.
client = TestClient(app)


# ---------- senha ----------

def test_login_confere_a_senha_pelo_hash_bcrypt():
    h = bcrypt.hashpw(b"Senha@123", bcrypt.gensalt()).decode()
    assert verificar_senha("Senha@123", h)
    assert not verificar_senha("errada", h)


def test_hash_falso_dos_dados_de_teste_nao_quebra_o_login():
    assert verificar_senha("qualquer", "HASH_FICTICIO_ANA") is False


# ---------- tokens ----------

def test_token_de_login_tem_tipo_e_jti():
    token, jti = criar_token_acesso(1, "ana@clinica.com")
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["tipo"] == TIPO_TOKEN_ACESSO
    assert payload["jti"] == jti
    assert payload["sub"] == "1"


def test_token_de_confirmacao_e_valido_so_para_confirmar():
    token = criar_token_confirmacao(3)
    assert validar_token_confirmacao(token) == 3
    login, _ = criar_token_acesso(3, "beatriz@clinica.com")
    with pytest.raises(ValueError):
        validar_token_confirmacao(login)


def test_token_de_confirmacao_nao_entra_no_sistema():
    token = criar_token_confirmacao(1)
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_token_assinado_com_outra_chave_e_recusado():
    falso = jwt.encode({"sub": "1", "tipo": "acesso", "jti": "x"}, "outra-chave", algorithm="HS256")
    r = client.get("/api/tutores", headers={"Authorization": f"Bearer {falso}"})
    assert r.status_code == 401


# ---------- protecao das rotas (enunciado 3.1) ----------

ROTAS_PRIVADAS = [
    ("get", "/api/tutores"),
    ("get", "/api/animais"),
    ("get", "/api/veterinarios"),
    ("post", "/api/veterinarios"),
    ("get", "/api/consultas"),
    ("get", "/api/vacinas"),
    ("get", "/api/especies"),
    ("get", "/api/racas"),
    ("get", "/api/cep/20040020"),
    ("post", "/api/animais/1/microchip"),
    ("get", "/api/animais/1/microchip/historico"),
    ("get", "/api/integracoes"),
    ("get", "/api/integracoes/resumo"),
    ("post", "/api/integracoes/1/reenviar"),
    ("get", "/api/auth/me"),
    ("post", "/api/auth/logout"),
]


@pytest.mark.parametrize("metodo,rota", ROTAS_PRIVADAS)
def test_rota_privada_sem_token_da_401(metodo, rota):
    r = getattr(client, metodo)(rota)
    assert r.status_code == 401, f"{metodo.upper()} {rota} deveria exigir login"


def test_todas_as_rotas_de_negocio_estao_protegidas():
    """Pega rota nova que alguem registrar sem protecao."""
    publicas = {"/health", "/api/auth/login", "/api/auth/solicitar-confirmacao", "/api/auth/confirmar-senha"}
    def chamadas(dependant):
        for d in dependant.dependencies:
            yield getattr(d.call, "__name__", "")
            yield from chamadas(d)

    abertas = [
        rota.path for rota in app.routes
        if getattr(rota, "path", "").startswith("/api") and rota.path not in publicas
        and "get_current_veterinario" not in set(chamadas(rota.dependant))
    ]
    assert abertas == []
