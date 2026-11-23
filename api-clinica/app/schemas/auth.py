from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Login(BaseModel):
    email: EmailStr = Field(examples=["ana@clinica.com"])
    senha: str = Field(min_length=1, examples=["Senha@123"])


class LoginResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class VeterinarioLogado(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_completo: str
    email: str
    crmv_numero: str
    crmv_uf: str
    situacao: str


class SolicitarConfirmacao(BaseModel):
    email: EmailStr = Field(examples=["beatriz@clinica.com"])


class ConfirmacaoSolicitada(BaseModel):
    email: str
    # Envio por e-mail simulado: o token do link volta aqui para os testes.
    token_confirmacao_simulado: str


class ConfirmarSenha(BaseModel):
    token: str
