
from unittest.mock import patch, Mock
from django.test import SimpleTestCase

from sistema.src.lozai_service import LozAIService


class LozAIServiceTests(SimpleTestCase):

    def setUp(self):
        self.service = LozAIService()
        self.maquina = Mock()
        self.maquina.id = 1
        self.maquina.nombre = "PC-Prueba"
        self.maquina.ip = "192.168.1.10"
        self.maquina.estado = "activa"

    @patch("sistema.src.lozai_service.GeminiProvider")
    def test_gemini_responde_correctamente(self, MockGemini):
        MockGemini.return_value.responder.return_value = "Respuesta Gemini"

        respuesta = self.service.responder(
            self.maquina,
            "Hola"
        )

        self.assertEqual(respuesta, "Respuesta Gemini")
        self.assertEqual(
            self.service.ultimo_proveedor,
            "Gemini"
        )

    @patch("sistema.src.lozai_service.GeminiProvider")
    def test_qwen_se_activa_si_gemini_falla(self, MockGemini):
        MockGemini.return_value.responder.side_effect = ValueError(
            "Gemini no disponible"
        )

        self.service._responder_con_qwen = Mock(
            return_value="Respuesta Qwen"
        )

        respuesta = self.service.responder(
            self.maquina,
            "Hola"
        )

        self.assertEqual(respuesta, "Respuesta Qwen")
        self.assertEqual(
            self.service.ultimo_proveedor,
            "Qwen3:14b"
        )

    @patch("sistema.src.lozai_service.GeminiProvider")
    def test_no_repetir_herramientas_tras_error(self, MockGemini):

        def fallar_despues_de_herramienta(*args, **kwargs):
            self.service.tool_executor.ejecuciones_realizadas = 1
            raise ValueError("Error después de ejecutar herramienta")

        MockGemini.return_value.responder.side_effect = (
            fallar_despues_de_herramienta
        )

        self.service._responder_con_qwen = Mock()

        with self.assertRaises(RuntimeError):
            self.service.responder(
                self.maquina,
                "Ejecutá un diagnóstico"
            )

        self.service._responder_con_qwen.assert_not_called()
