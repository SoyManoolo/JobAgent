from pydantic import BaseModel, field_validator, AnyUrl
from datetime import datetime
from typing import Optional, List, Dict


class OfertaCreate(BaseModel):
    # IDENTIFICACIÓN
    id: str
    id_plataforma: str
    plataforma: str
    url: str

    # INFORMACIÓN BÁSICA
    titulo: str
    empresa: str
    descripcion: str

    # OPCIONALES
    fecha_oferta: Optional[datetime] = None

    # VALIDACIONES
    @field_validator("url")
    @classmethod
    def validar_url(cls, v: str) -> str:
        AnyUrl(v)
        return v
