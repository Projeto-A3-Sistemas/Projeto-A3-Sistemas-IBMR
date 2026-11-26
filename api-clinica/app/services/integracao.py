"""Integração com a API governamental simulada (P3 - Milestone 4).

Fluxo (seção 7.4 dos requisitos e contrato em api-governo/README.md):

1. Uma ação na clínica cria uma comunicação PENDENTE em integracao_governo:
   - vínculo de microchip ......... cadastro_animal    (chave CAD-{id do vínculo})
   - atualização de animal c/ chip  atualizacao_animal (chave ATU-{animal}-{momento})
   - vacina antirrábica aplicada .. vacina_antirrabica (chave VAC-{id da vacina})
2. Logo depois da resposta ao usuário, a clínica tenta enviar (segundo plano).
3. Resultado:
   - 200/201 ................... confirmada (grava o protocolo do governo)
   - 4xx (dados recusados) ..... falha (corrigir e reenviar pelo botão)
   - 5xx, timeout, sem conexão . continua pendente (nova tentativa automática)
4. A mesma chave é usada em todas as tentativas, então o governo nunca duplica (RN12).
"""
import logging
import time
from datetime import datetime

import httpx
from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import GOVERNO_API_URL, GOVERNO_TIMEOUT_SEGUNDOS
from app.db.session import SessionLocal
from app.models import Animal, IntegracaoGoverno, Vacina, Veterinario, VinculoMicrochip

log = logging.getLogger("clinica.integracao")


class AguardandoDados(Exception):
    """Ainda falta algo na clínica para poder enviar (ex.: animal sem microchip)."""


class DadosInvalidos(Exception):
    """A comunicação não faz mais sentido (ex.: chip substituído antes do envio)."""


# ---------------------------------------------------------------- criação

def criar_pendencia(
    db: Session, animal_id: int, tipo: str, chave: str, vacina_id: int | None = None
) -> IntegracaoGoverno:
    """Cria a comunicação pendente (ou devolve a que já existe com a mesma chave)."""
    existente = db.scalar(select(IntegracaoGoverno).where(IntegracaoGoverno.chave_idempotencia == chave))
    if existente:
        return existente
    integracao = IntegracaoGoverno(
        animal_id=animal_id, vacina_id=vacina_id, tipo_operacao=tipo,
        chave_idempotencia=chave, situacao="pendente", tentativas=0,
    )
    db.add(integracao)
    db.flush()
    return integracao


def registrar_envio_antirrabica(db: Session, vacina: Vacina) -> IntegracaoGoverno | None:
    """Vacina antirrábica aplicada gera a comunicação ao governo (uma única vez)."""
    if not (vacina.antirrabica and vacina.situacao == "aplicada"):
        return None
    return criar_pendencia(
        db, animal_id=vacina.animal_id, tipo="vacina_antirrabica",
        chave=f"VAC-{vacina.id}", vacina_id=vacina.id,
    )


def registrar_atualizacao_animal(db: Session, animal: Animal) -> IntegracaoGoverno | None:
    """Animal com microchip ativo que mudou de dados: avisa o governo."""
    if not _chip_ativo(db, animal.id):
        return None
    return criar_pendencia(
        db, animal_id=animal.id, tipo="atualizacao_animal",
        chave=f"ATU-{animal.id}-{int(time.time() * 1000)}",
    )


# ---------------------------------------------------------------- montagem

def _chip_ativo(db: Session, animal_id: int) -> VinculoMicrochip | None:
    return db.scalar(select(VinculoMicrochip).where(
        VinculoMicrochip.animal_id == animal_id, VinculoMicrochip.situacao == "ativo"))


def _dados_animal(animal: Animal) -> dict:
    return {
        "nome": animal.nome,
        "especie": animal.especie.nome,
        "raca": animal.raca.nome if animal.raca else None,
        "sexo": animal.sexo,
        "data_nascimento": animal.data_nascimento.isoformat() if animal.data_nascimento else None,
        "tutor_nome": animal.tutor.nome_completo,
        "tutor_cpf": animal.tutor.cpf,
    }


def montar_requisicao(db: Session, integracao: IntegracaoGoverno) -> tuple[str, str, dict, dict]:
    """Devolve (método, caminho, corpo, cabeçalhos) para a API do governo."""
    animal = db.get(Animal, integracao.animal_id)
    cabecalhos = {"Idempotency-Key": integracao.chave_idempotencia}

    if integracao.tipo_operacao == "cadastro_animal":
        vinculo = db.get(VinculoMicrochip, int(integracao.chave_idempotencia.split("-")[1]))
        if not vinculo or vinculo.situacao != "ativo":
            raise DadosInvalidos("O microchip foi substituído antes do envio do cadastro.")
        corpo = {"microchip": vinculo.codigo_microchip, **_dados_animal(animal)}
        return "POST", "/api/governo/animais", corpo, cabecalhos

    chip = _chip_ativo(db, animal.id)
    if not chip:
        raise AguardandoDados("Animal sem microchip ativo. Vincule o microchip para enviar.")

    if integracao.tipo_operacao == "atualizacao_animal":
        return "PUT", f"/api/governo/animais/{chip.codigo_microchip}", _dados_animal(animal), cabecalhos

    if integracao.tipo_operacao == "vacina_antirrabica":
        vacina = db.get(Vacina, integracao.vacina_id)
        if not vacina or vacina.situacao != "aplicada":
            raise DadosInvalidos("A vacina não está mais como aplicada.")
        vet = db.get(Veterinario, vacina.veterinario_id)
        corpo = {
            "microchip": chip.codigo_microchip,
            "vacina": vacina.nome_vacina,
            "fabricante": vacina.fabricante,
            "lote": vacina.numero_lote,
            "data_aplicacao": vacina.data_aplicacao.isoformat(),
            "veterinario_nome": vet.nome_completo,
            "veterinario_crmv": vet.crmv_numero,
            "veterinario_crmv_uf": vet.crmv_uf,
            "animal": _dados_animal(animal),
        }
        return "POST", "/api/governo/vacinacoes-antirrabicas", corpo, cabecalhos

    raise DadosInvalidos(f"Tipo de operação desconhecido: {integracao.tipo_operacao}")


# ---------------------------------------------------------------- envio

def enviar(db: Session, integracao: IntegracaoGoverno) -> IntegracaoGoverno:
    """Tenta enviar UMA comunicação e grava o resultado."""
    if integracao.situacao == "confirmada":
        return integracao
    try:
        metodo, caminho, corpo, cabecalhos = montar_requisicao(db, integracao)
    except AguardandoDados as aviso:
        integracao.situacao, integracao.mensagem_erro = "pendente", str(aviso)
        db.commit()
        return integracao
    except DadosInvalidos as erro:
        integracao.situacao, integracao.mensagem_erro = "falha", str(erro)
        db.commit()
        return integracao

    integracao.situacao = "enviada"
    integracao.tentativas = (integracao.tentativas or 0) + 1
    db.commit()

    try:
        resposta = httpx.request(
            metodo, f"{GOVERNO_API_URL}{caminho}", json=corpo, headers=cabecalhos,
            timeout=GOVERNO_TIMEOUT_SEGUNDOS,
        )
    except httpx.TimeoutException:
        integracao.situacao = "pendente"
        integracao.mensagem_erro = f"Governo não respondeu em {GOVERNO_TIMEOUT_SEGUNDOS:g}s. Nova tentativa automática."
        db.commit()
        log.warning("integracao=%s timeout", integracao.id)
        return integracao
    except httpx.HTTPError:
        integracao.situacao = "pendente"
        integracao.mensagem_erro = "Governo indisponível (sem conexão). Nova tentativa automática."
        db.commit()
        log.warning("integracao=%s sem conexao", integracao.id)
        return integracao

    integracao.data_resposta = datetime.now()
    try:
        dados = resposta.json()
    except ValueError:
        dados = {}

    if resposta.status_code in (200, 201):
        integracao.situacao = "confirmada"
        integracao.protocolo_externo = dados.get("protocolo")
        integracao.mensagem_erro = None
    elif resposta.status_code >= 500:
        integracao.situacao = "pendente"
        integracao.mensagem_erro = (
            f"Governo indisponível ({resposta.status_code} {dados.get('codigo', '')}). Nova tentativa automática."
        ).replace(" )", ")")
    else:
        integracao.situacao = "falha"
        integracao.protocolo_externo = dados.get("protocolo")
        integracao.mensagem_erro = f"{dados.get('codigo', resposta.status_code)}: {dados.get('mensagem', resposta.text[:200])}"
    db.commit()
    log.info("integracao=%s situacao=%s protocolo=%s", integracao.id, integracao.situacao, integracao.protocolo_externo)
    return integracao


def enviar_por_id(integracao_id: int) -> None:
    """Usado em segundo plano: abre a própria conexão com o banco."""
    with SessionLocal() as db:
        integracao = db.get(IntegracaoGoverno, integracao_id)
        if integracao:
            enviar(db, integracao)


def enviar_em_segundo_plano(tarefas: BackgroundTasks, integracao_id: int | None) -> None:
    """Agenda o envio para logo depois de responder ao usuário."""
    if integracao_id:
        tarefas.add_task(enviar_por_id, integracao_id)


def processar_pendentes(db: Session) -> dict:
    """Reenvia todas as comunicações pendentes, da mais antiga para a mais nova."""
    pendentes = db.scalars(
        select(IntegracaoGoverno)
        .where(IntegracaoGoverno.situacao.in_(("pendente", "enviada")))
        .order_by(IntegracaoGoverno.id)
    ).unique().all()
    resumo = {"processadas": 0, "confirmadas": 0, "falhas": 0, "continuam_pendentes": 0}
    for integracao in pendentes:
        enviar(db, integracao)
        resumo["processadas"] += 1
        chave = {"confirmada": "confirmadas", "falha": "falhas"}.get(integracao.situacao, "continuam_pendentes")
        resumo[chave] += 1
    return resumo
