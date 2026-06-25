from sistema.src.tools.ping_tool import PingTool
from sistema.src.tools.diagnostico_tool import DiagnosticoTool

class ToolExecutor:
    def __init__(self):
        self.herramientas = {
            'ping': PingTool(),
            'diagnostico': DiagnosticoTool(),
        }

    def ejecutar(self, nombre_herramienta, maquina):
        herramienta = self.herramientas.get(nombre_herramienta)

        if not herramienta:
            return "Herramienta no encontrada."

        return herramienta.ejecutar(maquina)