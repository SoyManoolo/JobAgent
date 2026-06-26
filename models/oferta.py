from datetime import date, datetime
from sqlalchemy import JSON, Boolean, Date, String, DateTime, Enum, func, null
from sqlalchemy.orm import Mapped, MappedCollection, mapped_column
from database import Base
from enum import Enum as PyEnum
from typing import Optional


# Definimos las enumeraciones locales para tipo_trabajo y estado_oferta
class Tipo_trabajo(str, PyEnum):
    BACKEND = "backend"
    FULLSTACK = "fullstack"
    IA = "ia"


class Estado(str, PyEnum):
    DESCARTADO = "descartado"
    PENDIENTE_REVISION = "pendiente"
    APROBADO = "aprobado"
    APLICADO = "aplicado"


class Oferta(Base):
    __tablename__ = "ofertas"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    id_plataforma: Mapped[str] = mapped_column(String(100), nullable=False)
    plataforma: Mapped[str] = mapped_column(String(100), nullable=False)
    titulo: Mapped[str] = mapped_column(String(100), nullable=False)
    empresa: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(String, nullable=False)
    tipo_trabajo: Mapped[Tipo_trabajo] = mapped_column(
        Enum(Tipo_trabajo), nullable=False
    )
    estado: Mapped[Estado] = mapped_column(Enum(Estado), nullable=False)
    preguntas_formulario: Mapped[Optional[list[dict]]] = mapped_column(JSON)
    eliminado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_oferta: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_descubrimiento: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    fecha_aplicacion: Mapped[datetime] = mapped_column(DateTime)
    notas: Mapped[str] = mapped_column(String)
