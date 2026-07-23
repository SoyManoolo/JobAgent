"""Utilidad común para reintentar operaciones que pueden fallar temporalmente."""

import os
import time
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")

DEFAULT_RETRY_ATTEMPTS = max(1, int(os.getenv("RETRY_ATTEMPTS", "3")))
RETRY_DELAY_SECONDS = max(0, float(os.getenv("RETRY_DELAY_SECONDS", "1")))


def ejecutar_con_reintentos(
    operacion: Callable[[], T],
    descripcion: str,
    *,
    intentos: int = DEFAULT_RETRY_ATTEMPTS,
    no_reintentar: tuple[type[Exception], ...] = (),
) -> T:
    """Ejecuta una operación y vuelve a intentarla si falla temporalmente."""
    intentos = max(1, intentos)

    for intento in range(1, intentos + 1):
        try:
            return operacion()
        except no_reintentar:
            raise
        except Exception as error:
            if intento == intentos:
                raise

            print(
                f"Error en {descripcion} (intento {intento}/{intentos}): {error}. "
                "Reintentando...",
                flush=True,
            )
            time.sleep(RETRY_DELAY_SECONDS * intento)

    raise RuntimeError("No se pudo ejecutar la operación")
