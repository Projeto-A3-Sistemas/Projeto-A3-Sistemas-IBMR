"""Reenvio automático das comunicações pendentes (P3 - Milestone 4).

Roda em segundo plano enquanto a API está no ar. O intervalo vem de
INTEGRACAO_INTERVALO_SEGUNDOS (padrão 60; 0 desliga).
"""
import logging
import threading
from contextlib import asynccontextmanager

from app.core.config import INTEGRACAO_INTERVALO_SEGUNDOS
from app.db.session import SessionLocal
from app.services.integracao import processar_pendentes

log = logging.getLogger("clinica.reenvio")
_parar = threading.Event()


def _laco() -> None:
    while not _parar.wait(INTEGRACAO_INTERVALO_SEGUNDOS):
        try:
            with SessionLocal() as db:
                resumo = processar_pendentes(db)
            if resumo["processadas"]:
                log.info("reenvio automatico: %s", resumo)
        except Exception:
            log.exception("erro no reenvio automatico")


@asynccontextmanager
async def ciclo_de_vida(app):
    """Liga o reenvio quando a API sobe e desliga quando ela para."""
    thread = None
    if INTEGRACAO_INTERVALO_SEGUNDOS > 0:
        _parar.clear()
        thread = threading.Thread(target=_laco, name="reenvio-governo", daemon=True)
        thread.start()
    yield
    _parar.set()
    if thread:
        thread.join(timeout=2)
