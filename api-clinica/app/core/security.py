"""Senhas (bcrypt) e tokens JWT de login e de confirmação de senha (P1)."""
import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import JWT_SECRET

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

TIPO_TOKEN_ACESSO = "acesso"
TIPO_TOKEN_CONFIRMACAO = "confirmacao_senha"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), senha_hash.encode())
    except ValueError:
        # Hash que não é bcrypt (ex.: 'HASH_FICTICIO_ANA' dos dados de teste).
        return False


def criar_token_acesso(veterinario_id: int, email: str) -> tuple[str, str]:
    """Token de login. Devolve (token, jti); o jti é o que o logout revoga."""
    jti = str(uuid.uuid4())
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(veterinario_id),
        "tipo": TIPO_TOKEN_ACESSO,
        "email": email,
        "jti": jti,
        "iat": agora,
        "exp": agora + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM), jti


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as erro:
        raise ValueError("Token inválido ou expirado.") from erro


# Confirmação de senha: o "link" enviado por e-mail (simulado) é um token
# assinado com validade de 24 h. Assim não é preciso guardar código no banco.

def criar_token_confirmacao(veterinario_id: int) -> str:
    payload = {
        "sub": str(veterinario_id),
        "tipo": TIPO_TOKEN_CONFIRMACAO,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def validar_token_confirmacao(token: str) -> int:
    """Devolve o id do veterinário dono do token de confirmação."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as erro:
        raise ValueError("Link de confirmação inválido ou expirado.") from erro
    if payload.get("tipo") != TIPO_TOKEN_CONFIRMACAO:
        raise ValueError("Link de confirmação inválido.")
    return int(payload["sub"])
