"""Endereços com preenchimento automático pelo ViaCEP (P4 - Milestones 2 e 3, RF10, RF11).

O cadastro de tutor (P3) pede um endereco_id: este é o endpoint que cria esse endereço.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Endereco
from app.schemas.endereco import EnderecoAtualizar, EnderecoCriar, EnderecoResposta
from app.services.erros import tratar_erro_banco
from app.services.viacep import ViaCepClient, ViaCepErro

router = APIRouter(prefix="/api/enderecos", tags=["Endereços"])

OBRIGATORIOS = ("logradouro", "bairro", "cidade", "uf")


def _buscar(db: Session, endereco_id: int) -> Endereco:
    endereco = db.get(Endereco, endereco_id)
    if not endereco:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Endereço não encontrado.")
    return endereco


def _completar(dados: EnderecoCriar) -> dict:
    """Preenche pelo ViaCEP só o que não foi digitado.

    Se o ViaCEP falhar (CEP inexistente, timeout, fora do ar), o endereço é aceito
    desde que logradouro, bairro, cidade e UF tenham sido digitados (RF11).
    """
    valores = dados.model_dump()
    faltando = [c for c in OBRIGATORIOS if not valores.get(c)]
    if not faltando:
        return valores
    try:
        encontrado = ViaCepClient().consultar(dados.cep)
    except ViaCepErro as erro:
        raise HTTPException(erro.status_http, f"{erro.mensagem} Faltam: {', '.join(faltando)}.")
    for campo in (*OBRIGATORIOS, "codigo_ibge"):
        if not valores.get(campo):
            valores[campo] = encontrado.get(campo) or None
    faltando = [c for c in OBRIGATORIOS if not valores.get(c)]
    if faltando:
        # CEP geral de cidade: o ViaCEP não traz rua nem bairro.
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            f"Este CEP não traz o endereço completo. Preencha: {', '.join(faltando)}.")
    return valores


def _salvar(db: Session, endereco: Endereco) -> Endereco:
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(endereco)
    return endereco


@router.post("", response_model=EnderecoResposta, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: EnderecoCriar, db: Session = Depends(get_db)):
    """Cadastra o endereço. Basta enviar `cep` e `numero`; o resto vem do ViaCEP."""
    endereco = Endereco(**_completar(dados))
    db.add(endereco)
    return _salvar(db, endereco)


@router.get("/{endereco_id}", response_model=EnderecoResposta)
def consultar(endereco_id: int, db: Session = Depends(get_db)):
    return _buscar(db, endereco_id)


@router.put("/{endereco_id}", response_model=EnderecoResposta)
def atualizar(endereco_id: int, dados: EnderecoAtualizar, db: Session = Depends(get_db)):
    endereco = _buscar(db, endereco_id)
    for campo, valor in _completar(dados).items():
        setattr(endereco, campo, valor)
    return _salvar(db, endereco)
