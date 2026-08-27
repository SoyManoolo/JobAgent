from database import SessionLocal
from repositories import dashboard_repository, oferta_repository


## Función que obtiene estadísticas del dashboard, como el número total de ofertas, el número de ofertas procesadas y el número de ofertas pendientes de respuesta. Se utiliza una sesión de base de datos para realizar la consulta.
def obtener_stats():
    with SessionLocal() as db:
        return dashboard_repository.obtener_stats(db)

# Función que obtiene un resumen de las ofertas, incluyendo información como el ID de la oferta, el título, el estado y la fecha de creación. Se utiliza una sesión de base de datos para realizar la consulta.
def modificar_notas(id: str, notas: str):
    with SessionLocal() as db:
        return oferta_repository.modificar_notas(db, id, notas)
