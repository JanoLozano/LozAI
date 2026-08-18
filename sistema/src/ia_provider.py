import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from google.genai import types

load_dotenv()

# Clase que representa un proveedor de IA para generar respuestas a consultas técnicas sobre máquinas.
class IAProvider:
    # Inicializa el proveedor de IA, configurando la clave de API y los modelos disponibles.
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("No se configuró la variable de entorno GEMINI_API_KEY.")

        self.client = genai.Client(api_key=api_key)
        modelo_configurado = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self.modelos = list(
            dict.fromkeys(
                [
                    modelo_configurado,
                    "gemini-2.5-flash",
                ]
            )
        )
    # Guarda la función de herramienta para ser utilizada por el modelo de IA, permitiendo que el modelo ejecute herramientas específicas según sea necesario.
    def crear_funcion_para_gemini(self, herramienta, tool_executor, maquina):

        def funcion_tool() -> str:
            return tool_executor.ejecutar(
                herramienta.nombre,
                maquina
            )

        funcion_tool.__name__ = f"ejecutar_{herramienta.nombre}"
        funcion_tool.__doc__ = herramienta.descripcion

        return funcion_tool
    # Responde a una consulta técnica sobre una máquina específica, utilizando el modelo de IA y las herramientas disponibles para obtener información relevante.
    def responder(self, maquina, mensaje, tool_executor):

        funciones = []

        for herramienta in tool_executor.obtener_herramientas():
                funcion = self.crear_funcion_para_gemini(
                    herramienta,
                    tool_executor,
                    maquina
                )

                funciones.append(funcion)

        prompt = f"""
                Sos LozAI, un asistente técnico interno para soporte de equipos.

                Tu objetivo es ayudar al técnico a diagnosticar problemas y comprender
                el estado de la máquina seleccionada.

                MÁQUINA ACTUAL:
                - ID: {maquina.id}
                - Nombre: {maquina.nombre}
                - IP: {maquina.ip}
                - Estado registrado: {maquina.estado}

                REGLAS:
                - Podés utilizar tus conocimientos técnicos para explicar conceptos,
                interpretar resultados y recomendar acciones.
                - No inventes datos sobre la máquina actual.
                - Para conocer datos reales de la máquina que no estén incluidos arriba,
                utilizá una herramienta cuando sea necesario.
                - No ejecutes herramientas para saludos, conversación general o preguntas
                que puedan responderse sin consultar el equipo.
                - Ejecutá únicamente la herramienta necesaria para responder la consulta.
                - No ejecutes varias herramientas salvo que la consulta realmente requiera
                información de más de una.
                - Si no podés obtener un dato solicitado, indicá que no está disponible.
                - Respondé de forma clara, breve y orientada a soporte técnico.

                MENSAJE DEL TÉCNICO:
                {mensaje}
                """

        ultimo_error = None

        for model_name in self.modelos:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                    tools=funciones,

                    tool_config=types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(
                            mode="AUTO"
                        )
                    ),

                    thinking_config=types.ThinkingConfig(
                        thinking_budget=0
                    ),

                    max_output_tokens=300,
                    )
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
