from functools import wraps
from django.shortcuts import redirect
from sistema.models import Usuario

DASHBOARD_POR_ROL = {
    "admin": "dashboard_admin",
    "tecnico": "dashboard_tecnico",
    "usuario": "dashboard_usuario",
}

def obtener_usuario_actual(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return None

    usuario = Usuario.objects.filter(
        id=usuario_id,
        activo=True
    ).first()

    if usuario is None:
        request.session.flush()
        return None

    # Sincronizar la sesión con los datos actuales.
    request.session["usuario_nombre"] = usuario.nombre
    request.session["usuario_rol"] = usuario.role

    return usuario

def redirigir_segun_rol(request):
    usuario = obtener_usuario_actual(request)

    if usuario is None:
        return redirect("login")

    dashboard = DASHBOARD_POR_ROL.get(usuario.role)

    if dashboard is None:
        request.session.flush()
        return redirect("login")

    return redirect(dashboard)

def validar_roles(request, roles_permitidos):
    usuario = obtener_usuario_actual(request)

    if usuario is None:
        return redirect("login")

    if usuario.role not in roles_permitidos:
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

            if redireccion is not None:
                return redireccion

            return funcion(request, *args, **kwargs)

        return funcion_protegida

    return decorador
