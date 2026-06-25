import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from google.genai import types

load_dotenv()


class IAProvider:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("No se configuró la variable de entorno GEMINI_API_KEY.")

        self.client = genai.Client(api_key=api_key)
        modelo_configurado = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.modelos = list(
            dict.fromkeys(
                [
                    modelo_configurado,
                    "gemini-2.5-flash",
                    "gemini-2.5-flash-lite",
                ]
            )
        )

    def responder(self, maquina, mensaje, tool_executor):
        def ejecutar_ping() -> str:
            """Verifica la conectividad de red de la máquina seleccionada."""
            return tool_executor.ejecutar("ping", maquina)

        def ejecutar_diagnostico() -> str:
            """Realiza un diagnóstico básico de la máquina seleccionada."""
            return tool_executor.ejecutar("diagnostico", maquina)

        prompt = f"""
        Sos LozAI, un asistente técnico para soporte de máquinas.

        La máquina ya fue seleccionada por la URL del sistema.
        No le preguntes al usuario qué máquina quiere revisar.

        Máquina actual:
        - ID: {maquina.id}
        - Nombre: {maquina.nombre}
        - IP: {maquina.ip}
        - Estado: {maquina.estado}

        Podés usar estas herramientas cuando sean necesarias:
        - ejecutar_ping: para verificar conectividad.
        - ejecutar_diagnostico: para revisar información básica de la máquina.

        Respondé de forma clara, breve y útil.

        Mensaje del técnico:
        {mensaje}
        """

        ultimo_error = None

        for model_name in self.modelos:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[ejecutar_ping, ejecutar_diagnostico]
                    ),
                )
                break
            except (errors.ClientError, errors.ServerError) as error:
                ultimo_error = error
                codigo = getattr(error, "code", None)

                if codigo not in (404, 429, 503):
                    raise
        else:
            raise ultimo_error

        if not response.text:
            return "LozAI no pudo generar una respuesta para esta consulta."

        return response.text
