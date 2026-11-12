from django.shortcuts import render, redirect, get_object_or_404
from sistema.models import Usuario
from sistema.src.autorizacion import validar_roles
from django.views.decorators.http import require_POST

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

@require_POST
def cambiar_estado_usuario(request, usuario_id):
    redireccion = validar_roles(request, ["admin"])

    if redireccion is not None:
        return redireccion

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Impedir que el administrador desactive su propia cuenta.
    if usuario.id == request.session.get("usuario_id"):
        return redirect("listar_usuarios")

    usuario.activo = not usuario.activo
    usuario.save(update_fields=["activo"])

    return redirect("listar_usuarios")

