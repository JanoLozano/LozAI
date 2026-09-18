import requests


class OllamaProvider:
    def __init__(self):
        self.url = "http://localhost:11434/api/chat"
        self.modelo = "qwen3:14b"

    def _crear_tools(self, tool_executor):
        tools = []

        for herramienta in tool_executor.obtener_herramientas():
            tools.append({
                "type": "function",
                "function": {
                    "name": herramienta.nombre,
                    "description": herramienta.descripcion,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            })

        return tools

    def responder(self, maquina, mensaje, tool_executor):
        tools = self._crear_tools(tool_executor)

        system_prompt = f"""
Sos LozAI, un asistente técnico interno para soporte de equipos.

Tu objetivo es ayudar al técnico a diagnosticar problemas y comprender
el estado de la máquina seleccionada.

MÁQUINA ACTUAL:
- ID: {maquina.id}
- Nombre: {maquina.nombre}
- IP: {maquina.ip}
- Estado registrado: {maquina.estado}

REGLAS:
- Podés utilizar tus conocimientos técnicos para explicar conceptos.
- No inventes datos sobre la máquina.
- Para conocer datos reales de la máquina, utilizá una herramienta cuando sea necesario.
- No ejecutes herramientas para saludos o conversación general.
- Ejecutá únicamente la herramienta necesaria.
- No ejecutes varias herramientas salvo que sea realmente necesario.
- Respondé de forma clara, breve y orientada a soporte técnico.
"""

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": mensaje
            }
        ]

        payload = {
            "model": self.modelo,
            "messages": messages,
            "tools": tools,
            "stream": False
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()
        message = data["message"]

        messages.append(message)

        return {
            "message": message,
            "messages": messages,
            "tools": tools
        }

    def continuar_con_tool(self, messages, tools, nombre_tool, resultado):
        messages.append({
            "role": "tool",
            "tool_name": nombre_tool,
            "content": resultado
        })

        payload = {
            "model": self.modelo,
            "messages": messages,
            "tools": tools,
            "stream": False
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]