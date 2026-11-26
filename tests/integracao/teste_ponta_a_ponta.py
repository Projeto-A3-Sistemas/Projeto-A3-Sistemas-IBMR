"""Teste ponta a ponta do back end, seguindo os testes obrigatórios (seção 9 do enunciado).

Precisa das duas APIs no ar e do banco recém-criado:
    docker compose down -v && docker compose up --build
    pip install httpx
    python tests/integracao/teste_ponta_a_ponta.py

O teste 6 (CEP) usa o ViaCEP real e precisa de internet.
Rodar de novo exige recriar o banco (a Beatriz fica confirmada na primeira vez).
"""
import time
from datetime import date

import httpx

C = httpx.Client(base_url="http://localhost:8000", timeout=30, limits=httpx.Limits(max_keepalive_connections=0))
G = httpx.Client(base_url="http://localhost:8001", timeout=30)
ADMIN = {"X-Admin-Token": "admin-sdm"}
SENHA = "Senha@123"
HOJE = date.today().isoformat()
ESPERA_REENVIO = 90  # o reenvio automático roda a cada 60 s
ok_count = fail_count = 0


def check(nome, cond, extra=""):
    global ok_count, fail_count
    if cond:
        ok_count += 1
        print(f"  OK    {nome}")
    else:
        fail_count += 1
        print(f"  FALHA {nome}  {str(extra)[:300]}")


def falha(tipo, atraso=10):
    G.post("/api/governo/admin/modo-falha", json={"tipo": tipo, "atraso_segundos": atraso}, headers=ADMIN)


def login(email):
    return C.post("/api/auth/login", json={"email": email, "senha": SENHA})


def integracoes(animal_id, vacina_id=None):
    lista = C.get(f"/api/integracoes?animal_id={animal_id}", headers=H).json()
    return [i for i in lista if vacina_id is None or i["vacina_id"] == vacina_id]


def esperar(integracao_id, situacao, segundos):
    fim = time.time() + segundos
    while True:
        j = C.get(f"/api/integracoes/{integracao_id}", headers=H).json()
        if j["situacao"] == situacao or time.time() > fim:
            return j
        time.sleep(2)


print("== Testes 1 a 4: login")
r = login("ana@clinica.com")
check("T1 login de veterinária ativa e confirmada", r.status_code == 200, r.text)
H = {"Authorization": f"Bearer {r.json()['access_token']}"}
check("T2 veterinário inativo bloqueado (403)", login("carlos@clinica.com").status_code == 403)
check("T3 senha não confirmada bloqueada (403)", login("beatriz@clinica.com").status_code == 403)
r = C.post("/api/auth/login", json={"email": "ana@clinica.com", "senha": "errada"})
check("T4 senha incorreta rejeitada (401)", r.status_code == 401)

print("== Proteção dos endpoints (3.1)")
for rota in ("/api/tutores", "/api/animais", "/api/vacinas", "/api/integracoes", "/api/cep/20040020"):
    check(f"{rota} sem token -> 401", C.get(rota).status_code == 401)
check("/health continua público", C.get("/health").status_code == 200)

print("== Confirmação de senha (link simulado)")
r = C.post("/api/auth/solicitar-confirmacao", json={"email": "beatriz@clinica.com"})
tok_conf = r.json()["token_confirmacao_simulado"]
check("token de confirmação não serve como login",
      C.get("/api/auth/me", headers={"Authorization": f"Bearer {tok_conf}"}).status_code == 401)
check("confirmar senha", C.post("/api/auth/confirmar-senha", json={"token": tok_conf}).status_code == 200)
check("Beatriz entra depois de confirmar", login("beatriz@clinica.com").status_code == 200)

print("== Teste 5: tutor e CPF duplicado")
TUTOR = {"nome_completo": "Paula Teste", "data_nascimento": "1992-02-02", "email": "paula@email.com",
         "telefone": "21977776666", "endereco_id": 1, "cpf": "529.982.247-25"}
r = C.post("/api/tutores", json=TUTOR, headers=H)
check("T5 cadastra tutor", r.status_code == 201, r.text)
tutor_id = r.json()["id"]
check("T5 CPF duplicado rejeitado (409)", C.post("/api/tutores", json=TUTOR, headers=H).status_code == 409)

print("== Teste 6: CEP (ViaCEP real)")
r = C.get("/api/cep/20040020", headers=H)
check("T6 CEP válido", r.status_code == 200, r.text)
r = C.get("/api/cep/99999999", headers=H)
check("T6 CEP inexistente (404)", r.status_code == 404, r.text)

print("== Testes 7, 8 e 11: animal, microchip e cadastro no governo")
ANIMAL = {"nome": "Bidu", "data_nascimento": "2023-01-10", "sexo": "M", "tutor_id": tutor_id,
          "especie_id": 1, "raca_id": 2}
r = C.post("/api/animais", json=ANIMAL, headers=H)
check("T7 cadastra animal", r.status_code == 201, r.text)
animal_id = r.json()["id"]
chip = f"98511{int(time.time()) % 10**10:010d}"
MICROCHIP = {"codigo_microchip": chip, "veterinario_id": 1, "data_implantacao": HOJE}
r = C.post(f"/api/animais/{animal_id}/microchip", json=MICROCHIP, headers=H)
check("T7 vincula microchip", r.status_code == 201, r.text)
time.sleep(3)
lista = integracoes(animal_id)
check("T11 animal cadastrado no governo", lista and lista[0]["situacao"] == "confirmada", lista)
check("T11 governo tem o animal", G.get(f"/api/governo/animais/{chip}").status_code == 200)
r = C.post("/api/animais/3/microchip", json=MICROCHIP, headers=H)
check("T8 microchip já usado rejeitado (409)", r.status_code == 409, r.text)
C.put(f"/api/animais/{animal_id}", json={**ANIMAL, "nome": "Bidu II"}, headers=H)
time.sleep(3)
check("T11 atualização chega ao governo", G.get(f"/api/governo/animais/{chip}").json().get("nome") == "Bidu II")

print("== Testes 9 e 10: histórico clínico e vacinas")
CONSULTA = {"animal_id": animal_id, "veterinario_id": 1, "data_hora": f"{HOJE}T10:00:00",
            "motivo": "Check-up anual", "situacao": "realizada"}
check("T9 registra consulta", C.post("/api/consultas", json=CONSULTA, headers=H).status_code == 201)
check("T9 histórico do animal", len(C.get(f"/api/consultas?animal_id={animal_id}", headers=H).json()) == 1)

VAC = {"animal_id": animal_id, "veterinario_id": 1, "nome_vacina": "Rabisin", "tipo_vacina": "Antirrábica",
       "antirrabica": True, "fabricante": "Boehringer", "numero_lote": "L1", "data_aplicacao": HOJE,
       "dose": "Dose única", "data_proxima_dose": "2027-11-20", "validade_lote": "2027-06-30",
       "situacao": "aplicada"}
r = C.post("/api/vacinas", json=VAC, headers=H)
check("T10 registra vacina", r.status_code == 201, r.text)
v1 = r.json()["id"]
vacinas = C.get(f"/api/vacinas?animal_id={animal_id}", headers=H).json()
check("T10 histórico mostra a próxima dose", vacinas and vacinas[0]["data_proxima_dose"] == "2027-11-20", vacinas)

print("== Testes 12 e 13: comunicação obrigatória")
time.sleep(3)
lista = integracoes(animal_id, v1)
check("T12 antirrábica comunicada e confirmada com protocolo",
      lista and lista[0]["situacao"] == "confirmada" and lista[0]["protocolo_externo"], lista)
r = C.post("/api/vacinas", json={**VAC, "nome_vacina": "V10", "tipo_vacina": "Polivalente",
                                 "antirrabica": False, "numero_lote": "X"}, headers=H)
check("T13 não antirrábica não gera comunicação", integracoes(animal_id, r.json()["id"]) == [])

print("== Testes 14 e 15: indisponibilidade e reenvio automático (pode levar até 1 min)")
falha("INDISPONIVEL")
v2 = C.post("/api/vacinas", json={**VAC, "numero_lote": "L2"}, headers=H).json()["id"]
time.sleep(3)
check("T14 vacina gravada localmente", C.get(f"/api/vacinas/{v2}", headers=H).status_code == 200)
lista = integracoes(animal_id, v2)
check("T14 comunicação fica pendente", lista and lista[0]["situacao"] == "pendente", lista)
falha("DESLIGADO")
j = esperar(lista[0]["id"], "confirmada", ESPERA_REENVIO)
check("T15 reenvio automático confirma depois", j["situacao"] == "confirmada", j)

print("== Teste 16: repetição sem duplicidade")
falha("LENTO", 8)
v3 = C.post("/api/vacinas", json={**VAC, "numero_lote": "L3"}, headers=H).json()["id"]
time.sleep(7)
falha("DESLIGADO")
lista = integracoes(animal_id, v3)
time.sleep(4)
r = C.post(f"/api/integracoes/{lista[0]['id']}/reenviar", headers=H)
j = r.json() if r.status_code == 200 else esperar(lista[0]["id"], "confirmada", 10)
check("T16 reenvio depois do timeout confirma", j["situacao"] == "confirmada", j)
op = G.get(f"/api/governo/operacoes/{j['protocolo_externo']}").json()
check("T16 governo devolveu a operação original (sem duplicar)", op.get("tipo") == "VACINA_ANTIRRABICA", op)
check("T16 confirmada não é reenviada (409)",
      C.post(f"/api/integracoes/{lista[0]['id']}/reenviar", headers=H).status_code == 409)

print("== Logout")
check("logout", C.post("/api/auth/logout", headers=H).status_code == 200)
check("token encerrado não entra mais", C.get("/api/tutores", headers=H).status_code == 401)

print(f"\nRESULTADO: {ok_count} ok, {fail_count} falhas")
