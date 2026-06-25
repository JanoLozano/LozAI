from sistema.src.configuracion_sistema import ConfiguracionSistema


def configuracion_sistema(request):
    return {
        "configuracion_sistema": ConfiguracionSistema(),
    }
