"""Controle de acesso (P1 - Milestone 2): protege as rotas privadas no main.py."""
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import TIPO_TOKEN_ACESSO, decodificar_token
from app.db.session import get_db
from app.models import Veterinario
from app.models.token_revogado import TokenRevogado

# auto_error=False: sem o cabeçalho, responde 401 (o padrão do HTTPBearer é 403).
bearer = HTTPBearer(bearerFormat="JWT", auto_error=False)


def _nao_autenticado(mensagem: str) -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, mensagem)


def get_current_veterinario(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Veterinario:
    """Exige token de login válido e não revogado, de veterinário ativo e com senha confirmada."""
    if credenciais is None:
        raise _nao_autenticado("Faça login para acessar.")
    try:
        payload = decodificar_token(credenciais.credentials)
    except ValueError:
        raise _nao_autenticado("Token inválido ou expirado.")

    # Só o token de login dá acesso (o de confirmação de senha não).
    jti = payload.get("jti")
    if payload.get("tipo") != TIPO_TOKEN_ACESSO or not jti:
        raise _nao_autenticado("Token inválido ou expirado.")
    if db.get(TokenRevogado, jti):
        raise _nao_autenticado("Sessão encerrada. Faça login novamente.")

    vet = db.get(Veterinario, int(payload["sub"]))
    if not vet:
        raise _nao_autenticado("Veterinário não encontrado.")
    if vet.situacao != "ativo":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Veterinário inativo.")
    if not vet.senha_confirmada:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Senha ainda não confirmada.")
    return vet


def jti_e_expiracao(token: str) -> tuple[str, datetime]:
    payload = decodificar_token(token)
    return payload["jti"], datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
