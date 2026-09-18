from sistema.src.tool_executor import ToolExecutor
from sistema.src.providers.ollama_provider import OllamaProvider


class LozAIService:
    def __init__(self):
        self.tool_executor = ToolExecutor()
        self.ia_provider = OllamaProvider()

    def responder(self, maquina, mensaje):
        respuesta_modelo = self.ia_provider.responder(
            maquina=maquina,
            mensaje=mensaje,
            tool_executor=self.tool_executor
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

            message = self.ia_provider.continuar_con_tool(
                messages=messages,
                tools=tools,
                nombre_tool=nombre_tool,
                resultado=resultado
            )

        return message.get("content", "")