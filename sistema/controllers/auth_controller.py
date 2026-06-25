from django.shortcuts import render, redirect
from sistema.models import Usuario

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        usuario = Usuario.objects.filter(
            email=email,
            password=password,
            activo=True
        ).first()

        if usuario:
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nombre'] = usuario.nombre
            request.session['usuario_rol'] = usuario.role

            return redirect('dashboard')

        return render(request, 'login.html', {
            'error': 'Email o contraseña incorrectos.'
        })

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not nombre or not email or not password:
            return render(request, 'register.html', {
                'error': 'Todos los campos son obligatorios.'
            })

        if Usuario.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'Ya existe un usuario con ese email.'
            })

        Usuario.objects.create(
            nombre=nombre,
            email=email,
            password=password,
            role='usuario'
        )

        return redirect('login')

    return render(request, 'register.html')
