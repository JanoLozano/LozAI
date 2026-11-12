from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from sistema.models import Maquina
from sistema.src.autorizacion import validar_roles
from django.views.decorators.http import require_POST
from django.core.validators import validate_ipv46_address
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from sistema.models import Sesion

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

    if redireccion is not None:
        return redireccion

    template = "tecnico/maquinas.html"

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        ip = request.POST.get("ip", "").strip()
        estado = request.POST.get("estado", "activa").strip()

        if not nombre or not ip:
            return render(request, template, {
                "error": "El nombre y la dirección IP son obligatorios."
            })

        if len(nombre) > 100:
            return render(request, template, {
                "error": "El nombre no puede superar los 100 caracteres."
            })

        try:
            validate_ipv46_address(ip)
        except ValidationError:
            return render(request, template, {
                "error": "Ingresá una dirección IP válida."
            })

        if estado not in ["activa", "inactiva"]:
            return render(request, template, {
                "error": "El estado seleccionado no es válido."
            })

        if Maquina.objects.filter(nombre=nombre).exists():
            return render(request, template, {
                "error": "El nombre de la máquina ya existe."
            })

        if Maquina.objects.filter(ip=ip).exists():
            return render(request, template, {
                "error": "La dirección IP ya está registrada."
            })

        try:
            Maquina.objects.create(
                nombre=nombre,
                ip=ip,
                estado=estado
            )
        except IntegrityError:
            return render(request, template, {
                "error": "Ya existe una máquina con ese nombre o IP."
            })

        return redirect("listar_maquinas")

    return render(request, template)

# Editar máquina

def editar_maquina(request, maquina_id):
    redireccion = validar_roles(request, ["tecnico"])

    if redireccion is not None:
        return redireccion

    maquina = get_object_or_404(Maquina, id=maquina_id)
    template = "tecnico/maquinas.html"

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        ip = request.POST.get("ip", "").strip()
        estado = request.POST.get("estado", "").strip()

        contexto = {
            "maquina": maquina
        }

        # Campos obligatorios
        if not nombre or not ip:
            contexto["error"] = (
                "El nombre y la dirección IP son obligatorios."
            )
            return render(request, template, contexto)

        # Longitud del nombre
        if len(nombre) > 100:
            contexto["error"] = (
                "El nombre no puede superar los 100 caracteres."
            )
            return render(request, template, contexto)

        # Formato de dirección IP
        try:
            validate_ipv46_address(ip)
        except ValidationError:
            contexto["error"] = (
                "Ingresá una dirección IP válida."
            )
            return render(request, template, contexto)

        # Validar estado
        if estado not in ["activa", "inactiva"]:
            contexto["error"] = (
                "El estado seleccionado no es válido."
            )
            return render(request, template, contexto)

        # Comprobar nombre duplicado
        if Maquina.objects.filter(
            nombre=nombre
        ).exclude(id=maquina.id).exists():
            contexto["error"] = (
                "El nombre de la máquina ya existe."
            )
            return render(request, template, contexto)

        # Comprobar IP duplicada
        if Maquina.objects.filter(
            ip=ip
        ).exclude(id=maquina.id).exists():
            contexto["error"] = (
                "La dirección IP ya está registrada."
            )
            return render(request, template, contexto)

        # Guardar cambios
        maquina.nombre = nombre
        maquina.ip = ip
        maquina.estado = estado

        try:
            maquina.save(
                update_fields=["nombre", "ip", "estado"]
            )
        except IntegrityError:
            maquina.refresh_from_db()

            contexto["error"] = (
                "Ya existe una máquina con ese nombre o IP."
            )
            return render(request, template, contexto)

        return redirect("listar_maquinas")

    return render(request, template, {
        "maquina": maquina
    })


@require_POST
def eliminar_maquina(request, maquina_id):
    redireccion = validar_roles(request, ["tecnico"])

    if redireccion is not None:
        return redireccion

    with transaction.atomic():
        maquina = get_object_or_404(
            Maquina.objects.select_for_update(),
            id=maquina_id
        )

        maquina.activo = not maquina.activo
        maquina.save(update_fields=["activo"])

        if not maquina.activo:
            Sesion.objects.filter(
                maquina=maquina,
                fecha_fin__isnull=True
            ).update(
                fecha_fin=timezone.now()
            )

    return redirect("listar_maquinas")



    

        

    
