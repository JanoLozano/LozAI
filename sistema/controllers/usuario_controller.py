from django.shortcuts import render, redirect, get_object_or_404
from sistema.models import Usuario
from sistema.src.autorizacion import validar_roles

def listar_usuarios(request):
    redireccion = validar_roles(request, ["admin"])
    if redireccion:
        return redireccion

    usuarios = Usuario.objects.all().order_by('nombre')

    return render(request, 'admin/usuarios.html', {
        'usuarios': usuarios
    })

def editar_usuario(request, usuario_id):
    redireccion = validar_roles(request, ["admin"])
    if redireccion:
        return redireccion

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        usuario.nombre = request.POST.get('nombre')
        usuario.email = request.POST.get('email')
        usuario.role = request.POST.get('role')

        if not usuario.nombre or not usuario.email or not usuario.role:
            return render(request, 'admin/usuarios.html', {
                'usuario': usuario,
                'error': 'Todos los campos son obligatorios.'
            })

        usuario.save()
        return redirect('listar_usuarios')

    return render(request, 'admin/usuarios.html', {
        'usuario': usuario
    })

def cambiar_estado_usuario(request, usuario_id):
    redireccion = validar_roles(request, ["admin"])
    if redireccion:
        return redireccion

    usuario = get_object_or_404(Usuario, id=usuario_id)

    usuario.activo = not usuario.activo
    usuario.save()

    return redirect('listar_usuarios')
