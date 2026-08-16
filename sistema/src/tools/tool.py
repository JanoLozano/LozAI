from abc import ABC, abstractmethod


class Tool(ABC):

    nombre = ""
    descripcion = ""

    @abstractmethod
    def ejecutar(self, maquina):
        pass