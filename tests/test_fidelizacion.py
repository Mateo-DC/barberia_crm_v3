"""Smoke tests for attendance/promotion domain rules; run with python -m unittest."""

import tempfile
import unittest
from pathlib import Path

import backend.database.connection as connection_module
from backend.database.schema import init_db
from backend.repositories.clientes import crear_cliente
from backend.repositories.fidelizacion import (
    crear_promocion,
    registrar_asistencia,
    datos_dashboard,
)


class FidelizacionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        connection_module.DB_PATH = Path(self.temp.name) / "test.db"
        init_db()
        self.client_id = crear_cliente(
            "Cliente de prueba", "51911111111", "Nuevo", "2026-10-15"
        )

    def tearDown(self):
        self.temp.cleanup()

    def make_promo(self, **overrides):
        data = {
            "nombre": "Meta de prueba",
            "descripcion": "",
            "premio": "Corte gratis",
            "meta_visitas": 2,
            "modo_conteo": "acumuladas",
            "repeticion": "una_vez",
            "tipo_objetivo": "categoria",
            "objetivo": "Nuevo",
            "mensaje": "Hola {nombre}, {premio}",
            "fecha_inicio": None,
            "fecha_fin": None,
        }
        data.update(overrides)
        crear_promocion(data)

    def test_notificacion_se_crea_al_cumplir_meta(self):
        self.make_promo()
        self.assertEqual(registrar_asistencia(self.client_id, "2026-10-15"), 0)
        self.assertEqual(registrar_asistencia(self.client_id, "2026-10-16"), 1)
        notifications, pending = datos_dashboard()
        self.assertEqual(pending, 1)
        self.assertEqual(notifications[0]["promocion"], "Meta de prueba")

    def test_racha_se_reinicia_explicita(self):
        self.make_promo(modo_conteo="consecutivas", repeticion="recurrente")
        registrar_asistencia(self.client_id, "2026-10-15")
        registrar_asistencia(self.client_id, "2026-10-16", rompe_racha=True)
        # La visita marcada como ruptura inicia una nueva racha con una asistencia.
        self.assertEqual(registrar_asistencia(self.client_id, "2026-10-17"), 1)

    def test_categorias_no_objetivo_no_desbloquean(self):
        self.make_promo(objetivo="Premium")
        registrar_asistencia(self.client_id, "2026-10-15")
        registrar_asistencia(self.client_id, "2026-10-16")
        _, pending = datos_dashboard()
        self.assertEqual(pending, 0)


if __name__ == "__main__":
    unittest.main()
