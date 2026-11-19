"""Validacoes reutilizaveis (CPF, numeros etc.)."""
import re


def so_digitos(valor: str) -> str:
    """Remove pontos, tracos, espacos e parenteses: '529.982.247-25' -> '52998224725'."""
    return re.sub(r"\D", "", valor or "")


def cpf_valido(cpf: str) -> bool:
    """Confere os dois digitos verificadores do CPF."""
    cpf = so_digitos(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[tamanho]):
            return False
    return True
