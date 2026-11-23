"""Regression: Jinja templates, local-only editors, SQLite migration."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from jinja2 import Environment, FileSystemLoader

import backend.database.connection as db
from backend.database.schema import init_db
from backend.repositories.clientes import crear_cliente, obtener_cliente
from backend.repositories.fidelizacion import crear_promocion, obtener_promocion, registrar_asistencia
from backend.web import app


class WebWorkflowsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_path = db.DB_PATH
        db.DB_PATH = Path(self.temp.name) / 'test.sqlite'
        init_db()
        self.client = TestClient(app, raise_server_exceptions=True)
        self.client_id = crear_cliente('Cliente original', '51912345678', 'Nuevo', '2026-10-15')

    def tearDown(self):
        self.client.close()
        db.DB_PATH = self.old_path
        self.temp.cleanup()

    def test_templates_are_syntactically_valid(self):
        templates = Path(__file__).resolve().parents[1] / 'frontend' / 'templates'
        env = Environment(loader=FileSystemLoader(str(templates)))
        for file in templates.glob('*.html'):
            with self.subTest(template=file.name):
                env.get_template(file.name)

    def test_main_admin_routes_render(self):
        with patch('backend.web.is_host_request', return_value=True):
            for route in ('/', '/clientes', '/servicios', '/ventas', '/asistencias', '/fidelizacion', '/campanas'):
                with self.subTest(url=route):
                    response = self.client.get(route)
                    self.assertEqual(response.status_code, 200, response.text[:200])

    def test_local_editors_and_sales(self):
        with patch('backend.web.is_host_request', return_value=True):
            r = self.client.post(f'/clientes/{self.client_id}/editar', data={
                'nombre': 'Cliente editado', 'telefono': '51987654321', 'tipo_cliente': 'Premium'},
                follow_redirects=False)
            self.assertEqual(r.status_code, 303)
            self.assertEqual(obtener_cliente(self.client_id)['tipo_cliente'], 'Premium')
            r = self.client.post('/servicios', data={'nombre':'Corte urbano', 'precio':'30'})
            self.assertEqual(r.status_code, 200)
            self.assertIn('Corte urbano',r.text)
            r = self.client.post('/ventas', data={
                'cliente_id':self.client_id,'servicio':'Corte urbano','fecha':'2026-10-15','monto':'30',
                'campana':'Sin campaña'}, follow_redirects=False)
            self.assertEqual(r.status_code, 303)
            self.assertIn('Corte urbano', self.client.get('/ventas').text)
            self.assertEqual(obtener_cliente(self.client_id)['visitas_totales'], 0)
            # Reiniciar la BD no debe convertir la venta nueva en asistencia.
            init_db()
            with db.get_connection() as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM asistencias').fetchone()[0], 0)

    def test_promotion_editor_restricts_rules_with_achievements(self):
        datos={'nombre':'Premium 1','descripcion':'','premio':'Descuento','meta_visitas':1,
               'modo_conteo':'acumuladas','repeticion':'una_vez','tipo_objetivo':'categoria',
               'objetivo':'Nuevo','mensaje':'Hola {nombre}', 'fecha_inicio':None,'fecha_fin':None}
        crear_promocion(datos)
        registrar_asistencia(self.client_id,'2026-10-15')
        with patch('backend.web.is_host_request', return_value=True):
            r=self.client.post('/fidelizacion/promociones/1/editar',data={**datos,
                'meta_visitas':2,'fecha_inicio':'','fecha_fin':''})
            self.assertEqual(r.status_code,400)
            r=self.client.post('/fidelizacion/promociones/1/editar',data={**datos,
                'premio':'Corte gratis','fecha_inicio':'','fecha_fin':''},follow_redirects=False)
            self.assertEqual(r.status_code,303)
            self.assertEqual(obtener_promocion(1)['premio'],'Corte gratis')

    def test_remote_users_only_registration(self):
        with patch('backend.web.is_host_request', return_value=False):
            self.assertEqual(self.client.get('/registro').status_code,200)
            for url in ('/clientes','/servicios','/ventas','/fidelizacion','/campanas'):
                self.assertEqual(self.client.get(url).status_code,403)


if __name__ == '__main__':
    unittest.main()
