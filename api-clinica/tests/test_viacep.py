"""Testes do ViaCepClient sem internet (transporte HTTP falso). Teste 6 do enunciado.
Rodar na pasta api-clinica: pytest tests/test_viacep.py -v"""
import httpx
import pytest

from app.services.viacep import (CepInvalido, CepNaoEncontrado, ViaCepClient,
                                       ViaCepIndisponivel, ViaCepTimeout)

RESPOSTA_OK = {
    "cep": "20040-020", "logradouro": "Praça Pio X", "complemento": "", "bairro": "Centro",
    "localidade": "Rio de Janeiro", "uf": "RJ", "ibge": "3304557",
}


def cliente(handler) -> ViaCepClient:
    return ViaCepClient(http=httpx.Client(transport=httpx.MockTransport(handler)))


def test_cep_valido():
    dados = cliente(lambda req: httpx.Response(200, json=RESPOSTA_OK)).consultar("20040-020")
    assert dados["cidade"] == "Rio de Janeiro"
    assert dados["uf"] == "RJ"
    assert dados["codigo_ibge"] == "3304557"


@pytest.mark.parametrize("erro", [True, "true"])
def test_cep_inexistente(erro):
    c = cliente(lambda req: httpx.Response(200, json={"erro": erro}))
    with pytest.raises(CepNaoEncontrado):
        c.consultar("99999999")


def test_cep_mal_formatado_nem_chama_o_servico():
    chamadas = []
    c = cliente(lambda req: chamadas.append(req) or httpx.Response(200, json=RESPOSTA_OK))
    with pytest.raises(CepInvalido):
        c.consultar("123")
    assert chamadas == []


def test_timeout():
    def handler(req):
        raise httpx.ReadTimeout("demorou", request=req)
    with pytest.raises(ViaCepTimeout):
        cliente(handler).consultar("20040020")


def test_fora_do_ar():
    def handler(req):
        raise httpx.ConnectError("sem conexão", request=req)
    with pytest.raises(ViaCepIndisponivel):
        cliente(handler).consultar("20040020")


def test_erro_5xx():
    with pytest.raises(ViaCepIndisponivel):
        cliente(lambda req: httpx.Response(502)).consultar("20040020")
