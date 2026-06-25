class ConfiguracionSistema:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(ConfiguracionSistema, cls).__new__(cls)
            cls._instancia.nombre_sistema = "LozAI"
            cls._instancia.version = "1.0"

        return cls._instancia

    def obtener_nombre(self):
        return self.nombre_sistema

    def obtener_version(self):
        return self.version
    
    