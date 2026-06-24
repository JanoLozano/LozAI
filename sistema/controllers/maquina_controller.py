from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from sistema.models import Maquina

# Listar máquinas
def listar_maquinas(request):
    
    if request.session.get('usuario_rol') != 'tecnico':
        return redirect('login')
    
    maquinas = Maquina.objects.all()
    return render(request, 'maquinas/listar.html', {'maquinas': maquinas})

# Chat con máquina
def chat_maquina(request, maquina_id):

    if request.session.get('usuario_rol') != 'tecnico':
        return redirect('login')
    
    maquina = get_object_or_404(Maquina, id=maquina_id)
    return render(request, 'maquinas/chat.html', {'maquina': maquina})

# Crear máquina
def crear_maquina(request):
    if request.session.get('usuario_rol') != 'tecnico':
        return redirect('login')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        ip = request.POST.get('ip')
        estado = request.POST.get('estado')

        if not nombre: # Validación para el nombre
            return render(request, 'maquinas/crear.html', {'error': 'El nombre es obligatorio.'})

        if not ip: # Validación básica para la IP
            return render(request, 'maquinas/crear.html', {'error': 'La IP es obligatoria.'})

        if Maquina.objects.filter(nombre=nombre).exists():
            return render(request, 'maquinas/crear.html', {'error': 'El nombre de la máquina ya existe.'})

        if Maquina.objects.filter(ip=ip).exists():
            return render(request, 'maquinas/crear.html', {'error': 'La IP ya está en uso.'})
        
        Maquina.objects.create(nombre=nombre, ip=ip, estado=estado) # Creación de la máquina
        return redirect('listar_maquinas') # Redirigir a la lista de máquinas después de crear una nueva

    return render(request, 'maquinas/crear.html')

# Editar máquina
def editar_maquina(request, maquina_id):
    if request.session.get('usuario_rol') != 'tecnico':
        return redirect('login')
    
    maquina = get_object_or_404(Maquina, id=maquina_id)

    if request.method == 'POST':
        maquina.nombre = request.POST.get('nombre')
        maquina.ip = request.POST.get('ip')
        maquina.estado = request.POST.get('estado')
        
        if not maquina.nombre: # Validación básica para el nombre
            return render(request, 'maquinas/editar.html', {'maquina': maquina, 'error': 'El nombre es obligatorio.'})
        
        if not maquina.ip: # Validación básica para la IP
            return render(request, 'maquinas/editar.html', {'maquina': maquina, 'error': 'La IP es obligatoria.'})
        
        if Maquina.objects.filter(nombre=maquina.nombre).exclude(id=maquina.id).exists():
            return render(request, 'maquinas/editar.html', {'maquina': maquina, 'error': 'El nombre de la máquina ya existe.'})

        if Maquina.objects.filter(ip=maquina.ip).exclude(id=maquina.id).exists():
            return render(request, 'maquinas/editar.html', {'maquina': maquina, 'error': 'La IP ya está en uso.'})

        maquina.save()
        return redirect('listar_maquinas')

    return render(request, 'maquinas/editar.html', {'maquina': maquina})

def eliminar_maquina(request, maquina_id):
    if request.session.get('usuario_rol') != 'tecnico':
        return redirect('login')

    maquina = get_object_or_404(Maquina, id=maquina_id)

    maquina.activo = not maquina.activo
    maquina.save()
    
    return redirect('listar_maquinas')

    

        

    