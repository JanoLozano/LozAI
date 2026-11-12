
import logging
import httpx
from google.genai import errors
from sistema.src.tool_executor import ToolExecutor
from sistema.src.providers.gemini_provider import GeminiProvider
from sistema.src.providers.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)

class LozAIService:  
    def __init__(self):
        self.tool_executor = ToolExecutor()
        self.ollama_provider = OllamaProvider()
        self.ultimo_proveedor = None


    def responder(self, maquina, mensaje, historial=None):
        self.ultimo_proveedor = None

        try:
            gemini = GeminiProvider()

            respuesta = gemini.responder(
                maquina=maquina,
                mensaje=mensaje,
                tool_executor=self.tool_executor,
                historial=historial
            )

            self.ultimo_proveedor = "Gemini"

            logger.info("LozAI respondió mediante Gemini.")

            return respuesta

        except (
            errors.APIError,
            httpx.RequestError,
            TimeoutError,
            ConnectionError,
            ValueError
        ) as error:
            if self.tool_executor.ejecuciones_realizadas > 0:
                logger.error(
                "Gemini falló después de ejecutar una herramienta. "
                "Se cancela el respaldo para evitar repetir operaciones."
                )

                raise RuntimeError(
                    "La consulta falló después de ejecutar una herramienta."
                ) from error
            
            logger.warning(
                "Gemini falló. Activando Qwen: %s",
                error
            )

            respuesta = self._responder_con_qwen(
                maquina,
                mensaje,
                historial
            )

            if not respuesta or not respuesta.strip():
                raise ValueError("Qwen devolvió una respuesta vacía.")

            self.ultimo_proveedor = "Qwen3:14b"

            logger.info("LozAI respondió mediante Qwen3:14b.")

            return respuesta


    def _responder_con_qwen(self, maquina, mensaje, historial=None):
        respuesta_modelo = self.ollama_provider.responder(
            maquina=maquina,
            mensaje=mensaje,
            tool_executor=self.tool_executor,
            historial=historial
        )

        message = respuesta_modelo["message"]
        messages = respuesta_modelo["messages"]
        tools = respuesta_modelo["tools"]

        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            return message.get("content", "")

        for tool_call in tool_calls:
            nombre_tool = tool_call["function"]["name"]

            resultado = self.tool_executor.ejecutar(
                nombre_tool,
                maquina
            )

            message = self.ollama_provider.continuar_con_tool(
                messages=messages,
                tools=tools,
                nombre_tool=nombre_tool,
                resultado=resultado
            )

        return message.get("content", "")
