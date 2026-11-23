import unittest
from backend.domain.rules import MetaVisitas, cumple_meta, seleccionar
from backend.services.fidelizacion import calcular_ronda, personalizar_mensaje
from backend.security.access import public_registration_path
from backend.analytics.metrics import calcular_indicadores_ventas

class ConceptosTests(unittest.TestCase):
    def test_objeto_inmutable_y_regla_pura(self):
        meta = MetaVisitas(3, 'acumuladas')
        self.assertTrue(cumple_meta(3, meta))
        with self.assertRaises(Exception):
            meta.cantidad = 5
        self.assertEqual(calcular_ronda(6, 3, 'recurrente'), 2)

    def test_funcion_orden_superior(self):
        self.assertEqual(seleccionar([1,2,3,4], lambda x: x % 2 == 0), [2,4])

    def test_analitica_numpy_pandas(self):
        out = calcular_indicadores_ventas([{'monto': 10}, {'monto': 20}, {'monto': 30}])
        self.assertAlmostEqual(out['ticket_medio'], 20)
        self.assertAlmostEqual(out['mediana'], 20)

    def test_rutas_publicas(self):
        for path in ['/registro','/static/css/style.css']:
            self.assertTrue(public_registration_path(path))
        for path in ['/ventas', '/campanas', '/fidelizacion', '/openapi.json', '/static']:
            self.assertFalse(public_registration_path(path))

    def test_mensaje(self):
        texto = personalizar_mensaje('Hola {nombre} ganas {premio}',
            {'nombre':'Ana'}, {'nombre':'Promoción','premio':'corte','descripcion':'descuento', 'meta_visitas':3}, 1)
        self.assertIn('Ana',texto)
