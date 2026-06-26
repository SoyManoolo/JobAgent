from sqlalchemy.orm import Session
from models.oferta import Oferta


def obtener_stats(db: Session):
    query_base = db.query(Oferta).filter(Oferta.eliminado == False)

    total = query_base.count()

    pendientes = query_base.filter(Oferta.estado == "pendiente").count()
    aplicadas = query_base.filter(Oferta.estado == "aplicado").count()
    descartadas = query_base.filter(Oferta.estado == "descartado").count()
    return {
        "total_ofertas": total,
        "aplicadas": aplicadas,
        "pendientes": pendientes,
        "descartadas": descartadas,
    }


def modificar_notas(db: Session, id: str, nota: str):
    oferta = db.get(Oferta, id)

    if not oferta:
        return None

    oferta.notas = nota

    db.commit()

    db.refresh(oferta)

    return oferta
