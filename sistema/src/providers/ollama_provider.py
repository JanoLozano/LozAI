import requests

class OllamaProvider:
    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.modelo = "qwen3:14b"

    def responder(self, maquina, mensaje, tool_executor=None):
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
- Podés utilizar tus conocimientos técnicos para explicar conceptos.
- No inventes datos sobre la máquina.
- Respondé de forma clara, breve y orientada a soporte técnico.

MENSAJE DEL TÉCNICO:
{mensaje}
"""

        payload = {
            "model": self.modelo,
            "prompt": prompt,
            "stream": False,
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]