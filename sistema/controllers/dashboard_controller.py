from django.shortcuts import redirect, render


def dashboard(request):
    return render(request, 'dashboard.html')


def dashboard_admin(request):
    if request.session.get('usuario_rol') != 'admin':
        return redirect('login')

    return render(request, 'dashboards/admin.html')


def dashboard_tecnico(request):
    if request.session.get('usuario_rol') != 'tecnico':
        return redirect('login')

    return render(request, 'dashboards/tecnico.html')


def dashboard_usuario(request):
    if request.session.get('usuario_rol') != 'usuario':
        return redirect('login')

    return render(request, 'dashboards/usuario.html')