from sistema.src.tool_executor import ToolExecutor
from sistema.src.ia_provider import IAProvider


class LozAIService:
    def __init__(self):
        self.tool_executor = ToolExecutor()
        self.ia_provider = IAProvider()

    def responder(self, maquina, mensaje):
        return self.ia_provider.responder(
            maquina=maquina,
            mensaje=mensaje,
            tool_executor=self.tool_executor
        )