from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from sistema.models import Maquina
from sistema.src.autorizacion import validar_roles

# Listar máquinas
def listar_maquinas(request):
    redireccion = validar_roles(request, ["tecnico"])
    if redireccion:
        return redireccion
    
    maquinas = Maquina.objects.all()
    return render(request, 'tecnico/maquinas.html', {'maquinas': maquinas})

# Chat con máquina
def chat_maquina(request, maquina_id):
    redireccion = validar_roles(request, ["tecnico"])
    if redireccion:
        return redireccion
    
    maquina = get_object_or_404(Maquina, id=maquina_id)
    return render(request, 'tecnico/chat.html', {'maquina': maquina})

# Crear máquina
def crear_maquina(request):
    redireccion = validar_roles(request, ["tecnico"])
    if redireccion:
        return redireccion

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        ip = request.POST.get('ip')
        estado = request.POST.get('estado')

        if not nombre: # Validación para el nombre
            return render(request, 'tecnico/maquinas.html', {'error': 'El nombre es obligatorio.'})

        if not ip: # Validación básica para la IP
            return render(request, 'tecnico/maquinas.html', {'error': 'La IP es obligatoria.'})

        if Maquina.objects.filter(nombre=nombre).exists():
            return render(request, 'tecnico/maquinas.html', {'error': 'El nombre de la máquina ya existe.'})

        if Maquina.objects.filter(ip=ip).exists():
            return render(request, 'tecnico/maquinas.html', {'error': 'La IP ya está en uso.'})
        
        Maquina.objects.create(nombre=nombre, ip=ip, estado=estado) # Creación de la máquina
        return redirect('listar_maquinas') # Redirigir a la lista de máquinas después de crear una nueva

    return render(request, 'tecnico/maquinas.html')

# Editar máquina
def editar_maquina(request, maquina_id):
    redireccion = validar_roles(request, ["tecnico"])
    if redireccion:
        return redireccion
    
    maquina = get_object_or_404(Maquina, id=maquina_id)

    if request.method == 'POST':
        maquina.nombre = request.POST.get('nombre')
        maquina.ip = request.POST.get('ip')
        maquina.estado = request.POST.get('estado')
        
        if not maquina.nombre: # Validación básica para el nombre
            return render(request, 'tecnico/maquinas.html', {'maquina': maquina, 'error': 'El nombre es obligatorio.'})
        
        if not maquina.ip: # Validación básica para la IP
            return render(request, 'tecnico/maquinas.html', {'maquina': maquina, 'error': 'La IP es obligatoria.'})
        
        if Maquina.objects.filter(nombre=maquina.nombre).exclude(id=maquina.id).exists():
            return render(request, 'tecnico/maquinas.html', {'maquina': maquina, 'error': 'El nombre de la máquina ya existe.'})

        if Maquina.objects.filter(ip=maquina.ip).exclude(id=maquina.id).exists():
            return render(request, 'tecnico/maquinas.html', {'maquina': maquina, 'error': 'La IP ya está en uso.'})

        maquina.save()
        return redirect('listar_maquinas')

    return render(request, 'tecnico/maquinas.html', {'maquina': maquina})

def eliminar_maquina(request, maquina_id):
    redireccion = validar_roles(request, ["tecnico"])
    if redireccion:
        return redireccion

    maquina = get_object_or_404(Maquina, id=maquina_id)

    maquina.activo = not maquina.activo
    maquina.save()
    
    return redirect('listar_maquinas')

    

        

    
