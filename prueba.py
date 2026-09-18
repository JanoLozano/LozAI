from sistema.src.providers.ollama_provider import OllamaProvider


class MaquinaPrueba:
    id = 7
    nombre = "JANO"
    ip = "192.168.1.17"
    estado = "activo"


provider = OllamaProvider()

respuesta = provider.responder(
    maquina=MaquinaPrueba(),
    mensaje="¿Qué podés decirme de esta máquina con los datos disponibles?"
)

print(respuesta)