from models import Estado
from agent import llm
from repositories import oferta_repository
from database import SessionLocal


def procesar_ofertas_extraidas():
    with SessionLocal() as db:
        ofertas = oferta_repository.obtener_ofertas_estado(
            db, estado=Estado.EXTRAIDA, limite=25
        )

        total = len(ofertas)
        procesadas = 0
        errores = 0

        for oferta in ofertas:
            try:
                resultado = llm.analizar_oferta(oferta.descripcion)

                print("Resultado: ", resultado)

                if (
                    resultado["score_encaje"] < 20
                    or resultado["perfil_recomendado"] == "desconocido"
                ):
                    estado_final = Estado.DESCARTADA
                else:
                    estado_final = Estado.ANALIZADA

                datos_actualizar = {
                    "perfil_recomendado": resultado["perfil_recomendado"],
                    "idioma_oferta": resultado["idioma"],
                    "seniority": resultado["seniority"],
                    "score_backend": resultado["score_backend"],
                    "score_ia": resultado["score_ia"],
                    "score_encaje": resultado["score_encaje"],
                    "resumen": resultado["resumen"],
                    "motivo_encaje": resultado["motivo_encaje"],
                    "estado": estado_final,
                }

                oferta_repository.modificar_datos_oferta(
                    db, oferta.id, datos_actualizar
                )
                procesadas += 1

            except Exception as e:
                print(f"Error procesando la oferta {oferta.id}: {e}")

                oferta_repository.modificar_datos_oferta(
                    db, oferta.id, {"estado": Estado.ERROR}
                )

                errores += 1
            continue

    return {"total": total, "procesadas": procesadas, "errores": errores}
