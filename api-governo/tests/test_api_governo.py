"""Testes da API do governo: testes 11, 12, 14 e 16 do enunciado, do lado do serviço externo."""
import re
from datetime import date

from app.models import AnimalGoverno, Operacao, VacinacaoAntirrabica
from tests.conftest import ANIMAL, VACINA

ADMIN = {"X-Admin-Token": "token-teste"}
VAC = "/api/governo/vacinacoes-antirrabicas"


def cadastrar(client, **mudancas):
    return client.post("/api/governo/animais", json={**ANIMAL, **mudancas})


def vacinar(client, chave="VAC-10", **mudancas):
    return client.post(VAC, json={**VACINA, **mudancas}, headers={"Idempotency-Key": chave})


# ---------- animais (teste 11) ----------

def test_cadastra_e_consulta_animal(client):
    r = cadastrar(client)
    assert r.status_code == 201
    assert re.fullmatch(r"GOV-\d{4}-\d{4,}", r.json()["protocolo"])
    assert r.json()["mensagem"] == "Animal registrado"
    assert "SIMULADO" in r.json()["aviso"]

    r = client.get(f"/api/governo/animais/{ANIMAL['microchip']}")
    assert r.status_code == 200
    assert r.json()["tutor_cpf"] == "98765432100"


def test_protocolos_sao_sequenciais(client):
    p1 = cadastrar(client).json()["protocolo"]
    p2 = vacinar(client).json()["protocolo"]
    assert int(p2.rsplit("-", 1)[1]) == int(p1.rsplit("-", 1)[1]) + 1


def test_recadastro_igual_devolve_mesmo_protocolo(client):
    p1 = cadastrar(client).json()["protocolo"]
    r = cadastrar(client)
    assert r.status_code == 200
    assert r.json()["protocolo"] == p1 and r.json()["reprocessada"] is True


def test_microchip_duplicado_com_outros_dados(client):
    cadastrar(client)
    r = cadastrar(client, nome="Outro")
    assert r.status_code == 409
    assert r.json()["codigo"] == "MICROCHIP_JA_CADASTRADO"
    assert r.json()["protocolo"]  # a rejeição também ganha protocolo


def test_cpf_so_confere_formato(client):
    r = cadastrar(client, tutor_cpf="123.456")
    assert r.status_code == 422 and r.json()["codigo"] == "DADOS_INVALIDOS"
    # CPF dos dados de teste da clínica (Maria Silva): 11 dígitos, aceito
    assert cadastrar(client, tutor_cpf="12345678901").status_code == 201


def test_atualiza_animal(client):
    cadastrar(client)
    dados = {k: v for k, v in ANIMAL.items() if k != "microchip"} | {"nome": "Thor II"}
    r = client.put(f"/api/governo/animais/{ANIMAL['microchip']}", json=dados)
    assert r.status_code == 200 and r.json()["tipo"] == "ATUALIZACAO_ANIMAL"
    assert client.get(f"/api/governo/animais/{ANIMAL['microchip']}").json()["nome"] == "Thor II"


def test_atualiza_animal_inexistente(client):
    dados = {k: v for k, v in ANIMAL.items() if k != "microchip"}
    assert client.put("/api/governo/animais/000000000000", json=dados).status_code == 404


# ---------- vacinação e idempotência (testes 12 e 16) ----------

def test_vacinacao_exige_chave(client):
    cadastrar(client)
    assert client.post(VAC, json=VACINA).status_code == 422


def test_vacinacao_sem_animal_e_sem_dados_dele(client):
    r = vacinar(client)
    assert r.status_code == 422 and r.json()["codigo"] == "ANIMAL_NAO_CADASTRADO"


def test_vacinacao_cadastra_animal_junto(client, sessao):
    """Enunciado, seção 4, regra 2: vale mesmo se o animal não estava no governo."""
    dados_animal = {k: v for k, v in ANIMAL.items() if k != "microchip"}
    r = vacinar(client, animal=dados_animal)
    assert r.status_code == 201 and r.json()["tipo"] == "VACINA_ANTIRRABICA"
    assert client.get(f"/api/governo/animais/{ANIMAL['microchip']}").status_code == 200
    r2 = vacinar(client, animal=dados_animal)          # repetição: mesmo protocolo
    assert r2.status_code == 200 and r2.json()["protocolo"] == r.json()["protocolo"]
    assert sessao.query(AnimalGoverno).count() == 1


def test_repeticao_nao_duplica(client, sessao):
    cadastrar(client)
    r1, r2, r3 = vacinar(client), vacinar(client), vacinar(client)
    assert r1.status_code == 201
    assert r2.status_code == r3.status_code == 200
    assert r2.headers["Idempotent-Replayed"] == "true"
    assert r1.json()["protocolo"] == r2.json()["protocolo"] == r3.json()["protocolo"]
    assert sessao.query(VacinacaoAntirrabica).count() == 1


def test_mesma_chave_conteudo_diferente(client):
    cadastrar(client)
    vacinar(client)
    r = vacinar(client, lote="OUTRO")
    assert r.status_code == 409 and r.json()["codigo"] == "CHAVE_IDEMPOTENCIA_REUTILIZADA"


def test_chaves_parecidas_nao_se_confundem(client):
    cadastrar(client)
    p1 = vacinar(client, chave="VAC-1").json()["protocolo"]
    p10 = vacinar(client, chave="VAC-10", lote="L2").json()["protocolo"]
    assert p1 != p10
    assert vacinar(client, chave="VAC-1").json()["protocolo"] == p1


def test_rejeicao_nao_gasta_a_chave(client):
    assert vacinar(client).status_code == 422   # animal ainda não cadastrado
    cadastrar(client)                            # a clínica corrige...
    assert vacinar(client).status_code == 201   # ...e reenvia com a mesma chave


def test_aplicacao_futura(client):
    cadastrar(client)
    assert vacinar(client, data_aplicacao="2999-01-01").status_code == 422


def test_repeticao_dos_dados_de_teste(client, sessao):
    """Mesmo formato do 02_dados_teste.sql: reenviar VAC-1 devolve GOV-2026-0001."""
    sessao.add(AnimalGoverno(id=1, microchip="985112345678999", nome="Rex", especie="Cão", raca="Labrador",
                             sexo="M", data_nascimento=date(2020, 3, 15), tutor_nome="Maria Silva",
                             tutor_cpf="12345678901"))
    sessao.add(VacinacaoAntirrabica(id=1, animal_id=1, fabricante="Zoetis", lote="L2026A", vacina="Antirrábica",
                                    data_aplicacao=date(2026, 10, 20), veterinario_nome="Ana Lima",
                                    veterinario_crmv="12345/RJ", chave_idempotencia="VAC-1"))
    sessao.add(Operacao(id=1, protocolo="GOV-2026-0001", tipo="VACINA_ANTIRRABICA", situacao="PROCESSADA",
                        mensagem="Vacinação antirrábica registrada; microchip=985112345678999; chave=VAC-1"))
    sessao.commit()
    r = vacinar(client, chave="VAC-1", microchip="985112345678999", vacina="Antirrábica", fabricante="Zoetis",
                lote="L2026A", data_aplicacao="2026-10-20")
    assert r.status_code == 200 and r.json()["protocolo"] == "GOV-2026-0001"


# ---------- protocolo ----------

def test_consulta_por_protocolo(client):
    cadastrar(client)
    p = vacinar(client).json()["protocolo"]
    r = client.get(f"/api/governo/operacoes/{p}")
    assert r.status_code == 200
    assert r.json()["tipo"] == "VACINA_ANTIRRABICA"
    assert r.json()["microchip"] == ANIMAL["microchip"]
    assert client.get("/api/governo/operacoes/GOV-1999-9999").status_code == 404


# ---------- modo falha (teste 14) ----------

def test_modo_falha(client):
    r = client.post("/api/governo/admin/modo-falha", json={"tipo": "INDISPONIVEL"}, headers=ADMIN)
    assert r.status_code == 200 and r.json()["ativo"] is True
    assert cadastrar(client).status_code == 503
    assert client.get("/health").status_code == 200
    client.post("/api/governo/admin/modo-falha", json={"tipo": "DESLIGADO"}, headers=ADMIN)
    assert cadastrar(client).status_code == 201


def test_modo_falha_erro_validacao(client):
    client.post("/api/governo/admin/modo-falha", json={"tipo": "ERRO_VALIDACAO"}, headers=ADMIN)
    r = cadastrar(client)
    assert r.status_code == 422 and r.json()["codigo"] == "DADOS_INVALIDOS"


def test_modo_falha_exige_token(client):
    r = client.post("/api/governo/admin/modo-falha", json={"tipo": "INDISPONIVEL"},
                    headers={"X-Admin-Token": "errado"})
    assert r.status_code == 401
