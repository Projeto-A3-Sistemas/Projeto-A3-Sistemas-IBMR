"""Transforma erros do banco em respostas HTTP claras."""
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

# nome da regra no banco -> (codigo HTTP, mensagem)
MENSAGENS = {
    "tutor_cpf_key": (409, "Já existe um tutor com este CPF."),
    "veterinario_cpf_key": (409, "Já existe um veterinário com este CPF."),
    "veterinario_email_key": (409, "Já existe um veterinário com este e-mail."),
    "veterinario_crmv_numero_crmv_uf_key": (409, "Já existe um veterinário com este CRMV nesta UF."),
    "animal_raca_id_especie_id_fkey": (422, "A raça informada não pertence à espécie do animal."),
    "animal_check": (422, "Informe a data de nascimento ou a idade estimada."),
    "tutor_endereco_id_fkey": (422, "Endereço não encontrado."),
    "animal_tutor_id_fkey": (422, "Tutor não encontrado."),
    "animal_especie_id_fkey": (422, "Espécie não encontrada."),
}


def tratar_erro_banco(erro: IntegrityError) -> HTTPException:
    regra = getattr(getattr(erro.orig, "diag", None), "constraint_name", None)
    status, mensagem = MENSAGENS.get(regra, (422, "Os dados violam uma regra do banco."))
    return HTTPException(status_code=status, detail=mensagem)
