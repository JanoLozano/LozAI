from django.shortcuts import render, redirect, get_object_or_404
from sistema.models import Solicitud, Usuario, Maquina, SeguimientoTicket


def listar_tickets(request):
    if request.session.get('usuario_rol') != 'tecnico':
        return redirect('login')
    tickets = Solicitud.objects.all().order_by('-fecha_creacion')

    return render(request, 'tickets/listar_ticket.html', {
        'tickets': tickets
    })


def crear_ticket(request):
    rol = request.session.get('usuario_rol')
    usuario_logueado_id = request.session.get('usuario_id')

    if rol not in ['usuario', 'tecnico']:
        return redirect('login')

    usuarios = Usuario.objects.all()
    maquinas = Maquina.objects.all()

    if request.method == 'POST':
        maquina_id = request.POST.get('maquina')
        descripcion = request.POST.get('descripcion')

        if rol == 'tecnico':
            usuario_id = request.POST.get('usuario') # Para técnicos, se permite seleccionar un usuario para el ticket
        else:
            usuario_id = usuario_logueado_id

        if not usuario_id:
            return render(request, 'tickets/crear_ticket.html', {
                'usuarios': usuarios,
                'maquinas': maquinas,
                'rol': rol,
                'error': 'Debe seleccionar un usuario.'
            })

        if not descripcion:
            return render(request, 'tickets/crear_ticket.html', {
                'usuarios': usuarios,
                'maquinas': maquinas,
                'rol': rol,
                'error': 'La descripción es obligatoria.'
            })

        Solicitud.objects.create(
            usuario_id=usuario_id,
            maquina_id=maquina_id if maquina_id else None,
            descripcion=descripcion
        )

        if rol == 'usuario':
            return redirect('mis_tickets_usuario', usuario_id=usuario_id)

        return redirect('listar_tickets')

    return render(request, 'tickets/crear_ticket.html', {
        'usuarios': usuarios,
        'maquinas': maquinas,
        'rol': rol
    })


def detalle_ticket(request, ticket_id):
    tickets = Solicitud.objects.all().order_by('-fecha_creacion')
    ticket_seleccionado = get_object_or_404(Solicitud, id=ticket_id)

    seguimiento = SeguimientoTicket.objects.filter(
        ticket=ticket_seleccionado
    ).order_by('-fecha')

    return render(request, 'tickets/listar_ticket.html', {
        'tickets': tickets,
        'ticket_seleccionado': ticket_seleccionado,
        'seguimiento': seguimiento
    })


def cambiar_estado_ticket(request, ticket_id):
    ticket = get_object_or_404(Solicitud, id=ticket_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        comentario = request.POST.get('seguimiento')

        estado_anterior = ticket.estado
        ticket.estado = nuevo_estado
        ticket.save()

        if comentario or estado_anterior != nuevo_estado:
            SeguimientoTicket.objects.create(
                ticket=ticket,
                usuario=None,
                comentario=comentario if comentario else '',
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado
            )

    return redirect('detalle_ticket', ticket_id=ticket.id)

def mis_tickets_usuario(request, usuario_id):
    if request.session.get('usuario_id') != usuario_id:
        return redirect('dashboard_usuario')

    if request.session.get('usuario_rol') != 'usuario':
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    tickets = Solicitud.objects.filter(
        usuario=usuario
    ).order_by('-fecha_creacion')

    return render(request, 'tickets/listar_ticket.html', {
        'tickets': tickets,
        'usuario_actual': usuario,
        'modo_usuario': True
    })

def detalle_mi_ticket(request, usuario_id, ticket_id):
    if request.session.get('usuario_id') != usuario_id:
        return redirect('dashboard_usuario')
    
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

    return render(request, 'tickets/listar_ticket.html', {
        'tickets': tickets,
        'usuario_actual': usuario,
        'ticket_seleccionado': ticket_seleccionado,
        'seguimiento': seguimiento,
        'modo_usuario': True
    })