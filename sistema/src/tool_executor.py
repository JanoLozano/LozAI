from sistema.src.tools.ping_tool import PingTool
from sistema.src.tools.diagnostico_tool import DiagnosticoTool

class ToolExecutor:

    def __init__(self):
        tools = [
            PingTool(),
            DiagnosticoTool(),
        ]

        self.herramientas = {
            tool.nombre: tool
            for tool in tools
        }

        self.ejecuciones_realizadas = 0

    def ejecutar(self, nombre_herramienta, maquina):
        herramienta = self.herramientas.get(nombre_herramienta)

        if not herramienta:
            return "Herramienta no encontrada."

        self.ejecuciones_realizadas += 1

        return herramienta.ejecutar(maquina)

    def obtener_herramientas(self):
        return list(self.herramientas.values())