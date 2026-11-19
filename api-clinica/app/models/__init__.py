"""Models (tabelas) do banco da clinica.

Os models apenas MAPEIAM as tabelas criadas pelos scripts de db/clinica.
Eles nao criam nem alteram tabelas.
"""
from app.db.session import Base
from app.models.endereco import Endereco
from app.models.especie import Especie
from app.models.raca import Raca
from app.models.tutor import Tutor
from app.models.veterinario import Veterinario
from app.models.animal import Animal

__all__ = ["Base", "Endereco", "Especie", "Raca", "Tutor", "Veterinario", "Animal"]
