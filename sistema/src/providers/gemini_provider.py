
import os

from google import genai
from google.genai import types


class GeminiProvider:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada.")

        self.modelo = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )

        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=30000)
        )

    def _crear_tools(self, tool_executor):
        declaraciones = []

        for herramienta in tool_executor.obtener_herramientas():
            declaraciones.append(
                types.FunctionDeclaration(
                    name=herramienta.nombre,
                    description=herramienta.descripcion,
                    parameters_json_schema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                )
            )

        return types.Tool(
            function_declarations=declaraciones
        )

    def responder(
        self,
        maquina,
        mensaje,
        tool_executor=None,
        historial=None
    ):
        system_prompt = f"""
Sos LozAI, un asistente técnico interno para soporte de equipos.

MÁQUINA ACTUAL:
- ID: {maquina.id}
- Nombre: {maquina.nombre}
- IP: {maquina.ip}
- Estado registrado: {maquina.estado}

REGLAS:
- Respondé de forma clara, breve y técnica.
- No inventes información sobre la máquina.
- Para comprobar conectividad, utilizá ping.
- Para obtener datos de rendimiento, utilizá diagnostico.
- El diagnóstico de rendimiento se ejecuta en el servidor
  donde funciona Django, no en la máquina remota.
- No confundas datos del servidor con datos de la máquina.
- No ejecutes herramientas para saludos o consultas generales.
- Solicitá únicamente las herramientas necesarias.
- No afirmes haber ejecutado pruebas que no realizaste.
- Mantené el contexto de la conversación.
"""

        contenidos = []

        for item in historial or []:
            rol = (
                "model"
                if item["role"] == "assistant"
                else "user"
            )

            contenidos.append(
                types.Content(
                    role=rol,
                    parts=[
                        types.Part.from_text(
                            text=item["content"]
                        )
                    ]
                )
            )

        contenidos.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=mensaje)
                ]
            )
        )

        configuracion = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            tools=(
                [self._crear_tools(tool_executor)]
                if tool_executor is not None
                else None
            )
        )

        respuesta = self.client.models.generate_content(
            model=self.modelo,
            contents=contenidos,
            config=configuracion
        )

        herramientas_ejecutadas = set()

        for _ in range(2):
            llamadas = respuesta.function_calls or []

            if not llamadas:
                break

            if tool_executor is None:
                raise ValueError(
                    "Gemini solicitó herramientas no disponibles."
                )

            contenidos.append(
                respuesta.candidates[0].content
            )

            resultados = []

            for llamada in llamadas:
                nombre = llamada.name

                permitidas = {
                    herramienta.nombre
                    for herramienta
                    in tool_executor.obtener_herramientas()
                }

                if nombre not in permitidas:
                    resultado = "Herramienta no autorizada."

                elif nombre in herramientas_ejecutadas:
                    resultado = "La herramienta ya fue ejecutada."

                else:
                    resultado = tool_executor.ejecutar(
                        nombre,
                        maquina
                    )

                    herramientas_ejecutadas.add(nombre)

                resultados.append(
                    types.Part.from_function_response(
                        name=nombre,
                        response={"result": resultado}
                    )
                )

            contenidos.append(
                types.Content(
                    role="user",
                    parts=resultados
                )
            )

            respuesta = self.client.models.generate_content(
                model=self.modelo,
                contents=contenidos,
                config=configuracion
            )

        if respuesta.function_calls:
            raise ValueError(
                "Gemini superó el límite de llamadas a herramientas."
            )

        texto = respuesta.text

        if not texto or not texto.strip():
            raise ValueError(
                "Gemini devolvió una respuesta vacía."
            )

        return texto.strip()
