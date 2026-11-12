from django.shortcuts import render, redirect, get_object_or_404
from sistema.models import Solicitud, Usuario, Maquina, SeguimientoTicket
from sistema.src.autorizacion import validar_roles, redirigir_segun_rol
from django.db import transaction
from django.views.decorators.http import require_POST

def listar_tickets(request):
    redireccion = validar_roles(request, ["tecnico"])
    if redireccion:
        return redireccion
    tickets = Solicitud.objects.all().order_by('-fecha_creacion')

    return render(request, 'tecnico/tickets.html', {
        'tickets': tickets
    })

def crear_ticket(request):
    redireccion = validar_roles(request, ["usuario", "tecnico"])
    if redireccion is not None:
        return redireccion

    rol = request.session.get("usuario_rol")
    usuario_logueado_id = request.session.get("usuario_id")

    template = (
        "usuario/tickets.html"
        if rol == "usuario"
        else "tecnico/tickets.html"
    )

    usuarios = Usuario.objects.filter(activo=True)
    maquinas = Maquina.objects.filter(activo=True)

    contexto = {
        "usuarios": usuarios,
        "maquinas": maquinas,
        "rol": rol,
    }

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        maquina_id = request.POST.get("maquina")

        if rol == "tecnico":
            usuario_id = request.POST.get("usuario")
        else:
            usuario_id = usuario_logueado_id

        if not titulo or not descripcion or not maquina_id:
            contexto["error"] = "Todos los campos son obligatorios."
            return render(request, template, contexto)

        usuario = Usuario.objects.filter(
            id=usuario_id,
            activo=True
        ).first()

        maquina = Maquina.objects.filter(
            id=maquina_id,
            activo=True
        ).first()

        if usuario is None or maquina is None:
            contexto["error"] = (
                "El usuario o la máquina seleccionada no es válida."
            )
            return render(request, template, contexto)

        if len(titulo) > 200:
            contexto["error"] = (
                "El título no puede superar los 200 caracteres."
            )
            return render(request, template, contexto)

        Solicitud.objects.create(
            usuario=usuario,
            maquina=maquina,
            titulo=titulo,
            descripcion=descripcion,
            estado="pendiente"
        )

        if rol == "usuario":
            return redirect(
                "mis_tickets_usuario",
                usuario_id=usuario.id
            )

        return redirect("listar_tickets")

    return render(request, template, contexto)

def detalle_ticket(request, ticket_id):
    redireccion = validar_roles(request, ["tecnico"])
    if redireccion:
        return redireccion

    tickets = Solicitud.objects.all().order_by('-fecha_creacion')
    ticket_seleccionado = get_object_or_404(Solicitud, id=ticket_id)

    seguimiento = SeguimientoTicket.objects.filter(
        ticket=ticket_seleccionado
    ).order_by('-fecha')

    return render(request, 'tecnico/tickets.html', {
        'tickets': tickets,
        'ticket_seleccionado': ticket_seleccionado,
        'seguimiento': seguimiento
    })

@require_POST
def cambiar_estado_ticket(request, ticket_id):
    redireccion = validar_roles(request, ["tecnico"])

    if redireccion is not None:
        return redireccion

    estados_validos = [
        "pendiente",
        "en_proceso",
        "completada"
    ]

    nuevo_estado = request.POST.get("estado", "").strip()
    comentario = request.POST.get("seguimiento", "").strip()

    if nuevo_estado not in estados_validos:
        return redirect("detalle_ticket", ticket_id=ticket_id)

    tecnico = get_object_or_404(
        Usuario,
        id=request.session["usuario_id"],
        activo=True,
        role="tecnico"
    )

    with transaction.atomic():
        ticket = get_object_or_404(
            Solicitud.objects.select_for_update(),
            id=ticket_id
        )

        estado_anterior = ticket.estado

        if estado_anterior != nuevo_estado:
            ticket.estado = nuevo_estado
            ticket.save(update_fields=["estado"])

        if comentario or estado_anterior != nuevo_estado:
            SeguimientoTicket.objects.create(
                ticket=ticket,
                usuario=tecnico,
                comentario=comentario,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado
            )

    return redirect(
        "detalle_ticket",
        ticket_id=ticket_id
    )


def mis_tickets_usuario(request, usuario_id):
    redireccion = validar_roles(request, ["usuario"])
    if redireccion:
        return redireccion

    if request.session.get('usuario_id') != usuario_id:
        return redirigir_segun_rol(request)

    usuario = get_object_or_404(Usuario, id=usuario_id)

    tickets = Solicitud.objects.filter(
        usuario=usuario
    ).order_by('-fecha_creacion')

    return render(request, 'usuario/tickets.html', {
        'tickets': tickets,
        'usuario_actual': usuario,
        'modo_usuario': True
    })

def detalle_mi_ticket(request, usuario_id, ticket_id):
    redireccion = validar_roles(request, ["usuario"])
    if redireccion:
        return redireccion

    if request.session.get('usuario_id') != usuario_id:
        return redirigir_segun_rol(request)
    
    usuario = get_object_or_404(Usuario, id=usuario_id)

    tickets = Solicitud.objects.filter(
        usuario=usuario
    ).order_by('-fecha_creacion')

    ticket_seleccionado = get_object_or_404(
        Solicitud,
        id=ticket_id,
        usuario=usuario
    )

    seguimiento = SeguimientoTicket.objects.filter(
        ticket=ticket_seleccionado
    ).order_by('-fecha')

    return render(request, 'usuario/tickets.html', {
        'tickets': tickets,
        'usuario_actual': usuario,
        'ticket_seleccionado': ticket_seleccionado,
        'seguimiento': seguimiento,
        'modo_usuario': True
    })
