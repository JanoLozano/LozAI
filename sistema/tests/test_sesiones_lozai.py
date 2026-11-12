from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from sistema.models import (
    Usuario,
    Maquina,
    Sesion,
    MensajeSesion
)
from sistema.controllers.lozai_controller import obtener_contexto_chat

class SesionesLozAITests(TestCase):

    def setUp(self):
        self.tecnico = Usuario.objects.create(
            nombre="Tecnico Prueba",
            email="tecnico_prueba@lozai.test",
            password="password_test",
            role="tecnico",
            activo=True
        )

        self.maquina = Maquina.objects.create(
            nombre="PC-Test-LozAI",
            ip="192.168.50.10",
            estado="activa",
            activo=True
        )

        sesion_web = self.client.session
        sesion_web["usuario_id"] = self.tecnico.id
        sesion_web["usuario_rol"] = "tecnico"
        sesion_web.save()

    def test_reutiliza_sesion_abierta(self):
        request = self.client.get(
            f"/maquinas/{self.maquina.id}/chat/"
        ).wsgi_request

        _, _, primera = obtener_contexto_chat(
            request,
            self.maquina.id
        )

        _, _, segunda = obtener_contexto_chat(
            request,
            self.maquina.id
        )

        self.assertEqual(primera.id, segunda.id)
        self.assertEqual(
            Sesion.objects.filter(
                usuario=self.tecnico,
                maquina=self.maquina,
                fecha_fin__isnull=True
            ).count(),
            1
        )

    def test_cerrar_y_crear_nueva_sesion(self):
        primera = Sesion.objects.create(
            usuario=self.tecnico,
            maquina=self.maquina
        )

        respuesta = self.client.post(
            f"/maquinas/{self.maquina.id}/chat/cerrar/"
        )

        self.assertEqual(respuesta.status_code, 302)

        primera.refresh_from_db()
        self.assertIsNotNone(primera.fecha_fin)

        respuesta = self.client.get(
            f"/maquinas/{self.maquina.id}/chat/"
        )

        self.assertEqual(respuesta.status_code, 200)

        nueva = Sesion.objects.get(
            usuario=self.tecnico,
            maquina=self.maquina,
            fecha_fin__isnull=True
        )

        self.assertNotEqual(primera.id, nueva.id)

    @patch(
        "sistema.controllers.lozai_controller.LozAIService"
    )
    def test_envia_historial_a_la_ia(self, MockService):
        sesion = Sesion.objects.create(
            usuario=self.tecnico,
            maquina=self.maquina
        )

        MensajeSesion.objects.create(
            sesion=sesion,
            emisor="tecnico",
            contenido="Me llamo Juan."
        )

        MensajeSesion.objects.create(
            sesion=sesion,
            emisor="lozai",
            contenido="Hola Juan."
        )

        MockService.return_value.responder.return_value = (
            "Estás revisando una computadora."
        )
        MockService.return_value.ultimo_proveedor = "Gemini"

        respuesta = self.client.post(
            f"/maquinas/{self.maquina.id}/chat/enviar/",
            {"mensaje": "¿Qué estoy revisando?"}
        )

        self.assertEqual(respuesta.status_code, 200)

        argumentos = (
            MockService.return_value.responder.call_args.kwargs
        )

        self.assertEqual(
            argumentos["historial"],
            [
                {"role": "user", "content": "Me llamo Juan."},
                {"role": "assistant", "content": "Hola Juan."}
            ]
        )

        self.assertEqual(
            argumentos["mensaje"],
            "¿Qué estoy revisando?"
        )

    @patch(
        "sistema.controllers.lozai_controller.LozAIService"
    )
    def test_no_mezcla_sesiones(self, MockService):
        sesion_anterior = Sesion.objects.create(
            usuario=self.tecnico,
            maquina=self.maquina,
            fecha_fin=timezone.now()
        )

        MensajeSesion.objects.create(
            sesion=sesion_anterior,
            emisor="tecnico",
            contenido="Dato de la sesión anterior."
        )

        MockService.return_value.responder.return_value = (
            "Hola, ¿en qué puedo ayudarte?"
        )
        MockService.return_value.ultimo_proveedor = "Gemini"

        respuesta = self.client.post(
            f"/maquinas/{self.maquina.id}/chat/enviar/",
            {"mensaje": "Hola"}
        )

        self.assertEqual(respuesta.status_code, 200)

        argumentos = (
            MockService.return_value.responder.call_args.kwargs
        )

        self.assertEqual(
            argumentos["historial"],
            []
        )

        self.assertEqual(
            Sesion.objects.filter(
                usuario=self.tecnico,
                maquina=self.maquina
            ).count(),
            2
        )