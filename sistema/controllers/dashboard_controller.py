from django.shortcuts import redirect, render
from sistema.src.autorizacion import validar_roles, redirigir_segun_rol

def dashboard(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    return redirigir_segun_rol(request)


def dashboard_admin(request):
    redireccion = validar_roles(request, ["admin"])
    if redireccion:
        return redireccion

    return render(request, "dashboards/admin.html")


def dashboard_tecnico(request):
    redireccion = validar_roles(request, ["tecnico"])
    if redireccion:
        return redireccion

    return render(request, "dashboards/tecnico.html")


def dashboard_usuario(request):
    redireccion = validar_roles(request, ["usuario"])
    if redireccion:
        return redireccion

    return render(request, "dashboards/usuario.html")
