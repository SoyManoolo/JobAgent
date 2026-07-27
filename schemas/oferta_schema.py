from pydantic import BaseModel, field_validator, AnyUrl
from datetime import datetime
from typing import Optional


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
    ubicacion: str
    aplicacion_sencilla: bool

    # OPCIONALES
    salario: Optional[str] = None
    fecha_oferta: Optional[datetime] = None

    # VALIDACIONES
    @field_validator("url")
    @classmethod
    def validar_url(cls, v: str) -> str:
        AnyUrl(v)
        return v


class RespuestaFormularioUpdate(BaseModel):
    """Datos de una única respuesta modificada desde el dashboard."""

    respuesta: Optional[str] = None
    valor_seleccionado: Optional[str] = None
    informacion_suficiente: Optional[bool] = None
