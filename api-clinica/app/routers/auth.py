"""Login, logout e confirmação de senha (P1 - Milestone 2)."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    JWT_EXPIRE_MINUTES,
    criar_token_acesso,
    criar_token_confirmacao,
    validar_token_confirmacao,
    verificar_senha,
)
from app.db.session import get_db
from app.deps import bearer, get_current_veterinario, jti_e_expiracao
from app.models import Veterinario
from app.models.token_revogado import TokenRevogado
from app.schemas.auth import (
    ConfirmacaoSolicitada,
    ConfirmarSenha,
    Login,
    LoginResposta,
    SolicitarConfirmacao,
    VeterinarioLogado,
)

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


def _por_email(db: Session, email: str) -> Veterinario | None:
    return db.scalar(select(Veterinario).where(Veterinario.email == email.lower()))


@router.post("/login", response_model=LoginResposta)
def login(dados: Login, db: Session = Depends(get_db)):
    """Entra com e-mail e senha. Só veterinário ativo e com senha confirmada."""
    vet = _por_email(db, dados.email)
    # Mesma mensagem para e-mail inexistente e senha errada (não revela qual foi).
    if not vet or not verificar_senha(dados.senha, vet.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos.")
    if vet.situacao != "ativo":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Veterinário inativo.")
    if not vet.senha_confirmada:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Senha ainda não confirmada.")

    token, _ = criar_token_acesso(vet.id, vet.email)
    vet.ultimo_acesso = datetime.now(timezone.utc)
    db.commit()
    return LoginResposta(access_token=token, expires_in_minutes=JWT_EXPIRE_MINUTES)


@router.post("/logout")
def logout(
    credenciais: HTTPAuthorizationCredentials = Depends(bearer),
    _vet: Veterinario = Depends(get_current_veterinario),
    db: Session = Depends(get_db),
):
    """Encerra a sessão: o token deixa de valer mesmo antes de expirar."""
    jti, expira_em = jti_e_expiracao(credenciais.credentials)
    if not db.get(TokenRevogado, jti):
        db.add(TokenRevogado(jti=jti, expira_em=expira_em))
        db.commit()
    return {"detail": "Sessão encerrada."}


@router.get("/me", response_model=VeterinarioLogado)
def quem_esta_logado(vet: Veterinario = Depends(get_current_veterinario)):
    return vet


@router.post("/solicitar-confirmacao", response_model=ConfirmacaoSolicitada)
def solicitar_confirmacao(dados: SolicitarConfirmacao, db: Session = Depends(get_db)):
    """Gera o link de confirmação da senha de um veterinário já cadastrado.

    O envio por e-mail é simulado (enunciado 3.1): o token volta na resposta.
    """
    vet = _por_email(db, dados.email)
    if not vet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Veterinário não encontrado.")
    if vet.senha_confirmada:
        raise HTTPException(status.HTTP_409_CONFLICT, "Senha já confirmada.")
    return ConfirmacaoSolicitada(email=vet.email, token_confirmacao_simulado=criar_token_confirmacao(vet.id))


@router.post("/confirmar-senha")
def confirmar_senha(dados: ConfirmarSenha, db: Session = Depends(get_db)):
    """Confirma a senha pelo link e registra a data e hora da confirmação."""
    try:
        vet_id = validar_token_confirmacao(dados.token)
    except ValueError as erro:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(erro))
    vet = db.get(Veterinario, vet_id)
    if not vet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Veterinário não encontrado.")
    if vet.senha_confirmada:
        raise HTTPException(status.HTTP_409_CONFLICT, "Senha já confirmada.")
    vet.senha_confirmada = True
    vet.data_confirmacao = datetime.now(timezone.utc)
    db.commit()
    return {"detail": "Senha confirmada. Já é possível fazer login."}
