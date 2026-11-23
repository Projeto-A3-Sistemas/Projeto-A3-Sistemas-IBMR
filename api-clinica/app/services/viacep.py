"""Integração com o ViaCEP (P4 — Milestone 3, RF10/RF11).

Trata os três cenários exigidos:
  * CEP inexistente   -> CepNaoEncontrado   (a API responde 404)
  * Timeout (5 s)     -> ViaCepTimeout      (a API responde 504)
  * Fora do ar / 5xx  -> ViaCepIndisponivel (a API responde 503)
"""
import logging
import os
import time

import httpx
from fastapi import HTTPException

log = logging.getLogger("integracao.viacep")

VIACEP_URL = os.getenv("VIACEP_URL", "https://viacep.com.br/ws/{cep}/json/")
TIMEOUT_S = float(os.getenv("VIACEP_TIMEOUT", "5"))


class ViaCepErro(Exception):
    status_http = 502
    mensagem = "Erro ao consultar o ViaCEP."

    def __init__(self, mensagem: str | None = None):
        super().__init__(mensagem or self.mensagem)
        self.mensagem = mensagem or self.mensagem


class CepInvalido(ViaCepErro):
    status_http = 422
    mensagem = "CEP inválido: informe 8 dígitos."


class CepNaoEncontrado(ViaCepErro):
    status_http = 404
    mensagem = "CEP não encontrado. Preencha o endereço manualmente."


class ViaCepIndisponivel(ViaCepErro):
    status_http = 503
    mensagem = "Serviço de CEP indisponível no momento. Preencha o endereço manualmente."


class ViaCepTimeout(ViaCepIndisponivel):
    status_http = 504
    mensagem = "O serviço de CEP demorou para responder. Preencha o endereço manualmente."


_HTTP = httpx.Client(timeout=TIMEOUT_S)  # reaproveitado entre requisições


class ViaCepClient:
    def __init__(self, http: httpx.Client | None = None):
        # O cliente HTTP pode ser injetado (os testes usam um transporte falso).
        self.http = http or _HTTP

    def consultar(self, cep: str) -> dict:
        cep = "".join(c for c in cep if c.isdigit())
        if len(cep) != 8:
            raise CepInvalido()

        inicio = time.perf_counter()
        try:
            resp = self.http.get(VIACEP_URL.format(cep=cep), timeout=TIMEOUT_S)
        except httpx.TimeoutException:
            log.warning("ViaCEP timeout cep=%s", cep)
            raise ViaCepTimeout()
        except httpx.RequestError as e:
            log.warning("ViaCEP erro de conexão cep=%s erro=%s", cep, e)
            raise ViaCepIndisponivel()

        log.info("ViaCEP cep=%s status=%d tempo=%.0fms", cep, resp.status_code,
                 (time.perf_counter() - inicio) * 1000)
        if resp.status_code == 400:
            raise CepInvalido()
        if resp.status_code != 200:
            raise ViaCepIndisponivel()
        try:
            dados = resp.json()
        except ValueError:
            raise ViaCepIndisponivel()

        # O ViaCEP responde 200 com {"erro": true} (ou "true") quando o CEP não existe.
        if str(dados.get("erro", "")).lower() == "true":
            raise CepNaoEncontrado()

        return {
            "cep": cep,
            "logradouro": dados.get("logradouro", ""),
            "complemento": dados.get("complemento", ""),
            "bairro": dados.get("bairro", ""),
            "cidade": dados.get("localidade", ""),
            "uf": dados.get("uf", ""),
            "codigo_ibge": dados.get("ibge", ""),
        }


def consultar_cep(cep: str, cliente: ViaCepClient | None = None) -> dict:
    """Atalho para as rotas: converte os erros do ViaCEP em resposta HTTP."""
    try:
        return (cliente or ViaCepClient()).consultar(cep)
    except ViaCepErro as erro:
        raise HTTPException(erro.status_http, erro.mensagem)
