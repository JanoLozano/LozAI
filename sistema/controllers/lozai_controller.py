from django.shortcuts import render, redirect, get_object_or_404
from sistema.models import Maquina, Sesion, MensajeSesion, Usuario
from sistema.src.lozai_service import LozAIService
from sistema.src.autorizacion import validar_roles

def chat_lozai(request, maquina_id):
    redireccion = validar_roles(request, ["tecnico"])
    if redireccion:
        return redireccion

    maquina = get_object_or_404(Maquina, id=maquina_id)
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))

    sesion, creada = Sesion.objects.get_or_create(
        usuario=usuario,
        maquina=maquina,
        fecha_fin=None
    )

    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')

        if mensaje:
            MensajeSesion.objects.create(
                sesion=sesion,
                emisor='tecnico',
                contenido=mensaje
            )

            try:
                service = LozAIService()
                respuesta = service.responder(maquina, mensaje)
            except Exception as error:
                respuesta = (
                    "LozAI no pudo responder en este momento. "
                    f"Detalle técnico: {error}"
                )

            MensajeSesion.objects.create(
                sesion=sesion,
                emisor='lozai',
                contenido=respuesta
            )

        return redirect('chat_maquina', maquina_id=maquina.id)

    mensajes = MensajeSesion.objects.filter(
        sesion=sesion
    ).order_by('fecha')

    return render(request, 'tecnico/chat.html', {
        'maquina': maquina,
        'sesion': sesion,
        'mensajes': mensajes
    })
