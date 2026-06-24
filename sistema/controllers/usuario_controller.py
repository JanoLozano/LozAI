from django.shortcuts import render, redirect, get_object_or_404
from sistema.models import Usuario

def listar_usuarios(request):
    if request.session.get('usuario_rol') != 'admin':
        return redirect('login')

    usuarios = Usuario.objects.all().order_by('nombre')

    return render(request, 'usuarios/listar_usuario.html', {
        'usuarios': usuarios
    })

def editar_usuario(request, usuario_id):
    if request.session.get('usuario_rol') != 'admin':
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        usuario.nombre = request.POST.get('nombre')
        usuario.email = request.POST.get('email')
        usuario.role = request.POST.get('role')

        if not usuario.nombre or not usuario.email or not usuario.role:
            return render(request, 'usuarios/editar_usuario.html', {
                'usuario': usuario,
                'error': 'Todos los campos son obligatorios.'
            })

        usuario.save()
        return redirect('listar_usuarios')

    return render(request, 'usuarios/editar_usuario.html', {
        'usuario': usuario
    })

def cambiar_estado_usuario(request, usuario_id):
    if request.session.get('usuario_rol') != 'admin':
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    usuario.activo = not usuario.activo
    usuario.save()

    return redirect('listar_usuarios')