from datetime import datetime, timedelta
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import Base
from models.oferta import Estado, Oferta, OrdenOfertas
from repositories.oferta_repository import devolver_ofertas


class OfferPaginationTest(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        self.addCleanup(self.engine.dispose)
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.addCleanup(self.db.close)
        for index in range(107):
            estado = {105: Estado.APLICADA, 106: Estado.DESCARTADA}.get(index, Estado.EXTRAIDA)
            self.db.add(Oferta(
                id=f"{index:03}",
                id_plataforma=str(index),
                plataforma="test",
                url="https://example.com/oferta",
                titulo="Oferta",
                empresa="Test",
                descripcion="Oferta de prueba",
                estado=estado,
                fecha_descubrimiento=datetime(2026, 1, 1) - timedelta(days=index),
                score_encaje=index % 3,
            ))
        self.db.commit()

    def test_exclusions_apply_before_counting_and_paging(self):
        filtros = {
            "orden": OrdenOfertas.FECHA,
            "excluir_estados": [Estado.APLICADA, Estado.DESCARTADA],
        }
        primera, total = devolver_ofertas(self.db, pagina=1, **filtros)
        ultima, total_ultima = devolver_ofertas(self.db, pagina=11, **filtros)
        self.assertEqual((total, total_ultima), (105, 105))
        self.assertEqual([oferta.id for oferta in primera], [f"{index:03}" for index in range(10)])
        self.assertEqual([oferta.id for oferta in ultima], ["100", "101", "102", "103", "104"])

    def test_sorting_uses_id_to_break_ties_across_pages(self):
        primera, total = devolver_ofertas(self.db, pagina=1, orden=OrdenOfertas.SCORE)
        segunda, _ = devolver_ofertas(self.db, pagina=2, orden=OrdenOfertas.SCORE)
        esperado = [f"{index:03}" for index in range(104, 45, -3)]
        self.assertEqual(total, 107)
        self.assertEqual([oferta.id for oferta in primera + segunda], esperado)
