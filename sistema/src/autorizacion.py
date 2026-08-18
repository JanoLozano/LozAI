from django.shortcuts import redirect
from functools import wraps

DASHBOARD_POR_ROL = {
    "admin": "dashboard_admin",
    "tecnico": "dashboard_tecnico",
    "usuario": "dashboard_usuario",
}

def redirigir_segun_rol(request):
    rol = request.session.get("usuario_rol")
    dashboard = DASHBOARD_POR_ROL.get(rol)

    if dashboard:
        return redirect(dashboard)

    return redirect("login")

def validar_roles(request, roles_permitidos):
    if request.session.get("usuario_rol") not in roles_permitidos:
        return redirigir_segun_rol(request)

    return None

def requiere_roles(roles_permitidos):

    def decorador(funcion):

        @wraps(funcion)
        def funcion_protegida(request, *args, **kwargs):

            redireccion = validar_roles(
                request,
                roles_permitidos
            )

            if redireccion:
                return redireccion

            return funcion(request, *args, **kwargs)

        return funcion_protegida

    return decorador
