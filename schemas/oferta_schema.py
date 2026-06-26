from pydantic import AnyUrl, BaseModel, field_validator
from datetime import datetime
from typing import Optional, List, Dict


class OfertaCreate(BaseModel):
    id: str
    id_plataforma: str
    plataforma: str
    titulo: str
    empresa: str
    url: str
    descripcion: str
    tipo_trabajo: str
    estado: str = "pendiente"
    preguntas_formulario: Optional[List[Dict]] = None
    fecha_oferta: datetime
    fecha_aplicacion: Optional[datetime] = None
    notas: Optional[str] = None


@field_validator("url")
@classmethod
def validar_url(cls, v: str) -> str:
    AnyUrl(v)
    return v
