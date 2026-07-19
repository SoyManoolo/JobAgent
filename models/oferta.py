from datetime import datetime
from sqlalchemy import JSON, Boolean, Integer, String, DateTime, Enum, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from enum import Enum as PyEnum
from typing import Optional


class Estado(str, PyEnum):
    EXTRAIDA = "extraida"  # viene del scraping
    ANALIZADA = "analizada"  # ya tiene resultado de IA

    PENDIENTE_RESPUESTAS = "pendientes_respuestas"  # tiene preguntas pendientes de responder
    LISTA_PARA_APLICAR = "lista_para_aplicar"  # aprobada por ti

    APLICADA = "aplicada"
    DESCARTADA = "descartada"

    ERROR = "error"  # fallo en scraping / IA / parseo


class PerfilRecomendado(str, PyEnum):
    BACKEND = "backend"
    IA = "ia"
    DESCONOCIDO = "desconocido"


class Oferta(Base):
    __tablename__ = "ofertas"

    # IDENTIFICACIÓN
    id: Mapped[str] = mapped_column(String, primary_key=True)
    id_plataforma: Mapped[str] = mapped_column(String(100), nullable=False)
    plataforma: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(200), nullable=False)

    # INFORMACIÓN BÁSICA
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    empresa: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    salario: Mapped[str] = mapped_column(String, nullable=True)
    ubicacion: Mapped[str] = mapped_column(String, nullable=True)

    # ESTADO Y CONTROL
    estado: Mapped[Estado] = mapped_column(Enum(Estado), nullable=False)
    eliminado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notas: Mapped[Optional[str]] = mapped_column(Text)

    # FECHAS
    # fecha_oferta: Mapped[Optional[datetime]] = mapped_column(DateTime)
    fecha_descubrimiento: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    fecha_aplicacion: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # FORMULARIO
    aplicacion_sencilla: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    preguntas_formulario: Mapped[Optional[list[dict]]] = mapped_column(JSON)
    respuestas_formulario: Mapped[Optional[list[dict]]] = mapped_column(JSON)

    # CLASIFICACIÓN IA
    perfil_recomendado: Mapped[Optional[PerfilRecomendado]] = mapped_column(
        Enum(PerfilRecomendado)
    )
    idioma_oferta: Mapped[Optional[str]] = mapped_column(String(10))
    seniority: Mapped[Optional[str]] = mapped_column(String(50))

    # SCORES
    score_backend: Mapped[Optional[int]] = mapped_column(Integer)
    score_ia: Mapped[Optional[int]] = mapped_column(Integer)
    score_encaje: Mapped[Optional[int]] = mapped_column(Integer)

    # CONTENIDO IA
    keywords: Mapped[Optional[list[str]]] = mapped_column(JSON)
    resumen: Mapped[Optional[str]] = mapped_column(Text)
    motivo_encaje: Mapped[Optional[str]] = mapped_column(Text)
