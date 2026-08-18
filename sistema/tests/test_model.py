from django.test import TestCase

from sistema.models import Maquina

class MaquinaTest(TestCase):

    def test_crear_maquina(self):
        maquina = Maquina.objects.create(
            nombre="PC-Test",
            ip="192.168.1.100",
            estado="activa",
            activo=True
        )

        self.assertEqual(maquina.nombre, "PC-Test")
        self.assertEqual(maquina.ip, "192.168.1.100")
        self.assertEqual(maquina.estado, "activa")
        self.assertTrue(maquina.activo)