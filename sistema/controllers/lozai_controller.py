from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from sistema.models import Maquina, Sesion, MensajeSesion, Usuario
from sistema.src.lozai_service import LozAIService
from sistema.src.autorizacion import requiere_roles

def obtener_contexto_chat(request, maquina_id):
    maquina = get_object_or_404(Maquina, id=maquina_id)

    usuario = get_object_or_404(
        Usuario,
        id=request.session.get("usuario_id")
    )

    sesion, _ = Sesion.objects.get_or_create(
        usuario=usuario,
        maquina=maquina,
        fecha_fin=None
    )

    return maquina, usuario, sesion

# Vista para mostrar la interfaz de chat con LozAI
@requiere_roles(["tecnico"])
def chat_lozai(request, maquina_id):
    
    #  Contexto del chat, incluyendo la máquina, el usuario y la sesión
    maquina, usuario, sesion = obtener_contexto_chat(
        request,
        maquina_id
    )

    mensajes = MensajeSesion.objects.filter(
        sesion=sesion
    ).order_by("fecha")

    return render(
        request,
        "tecnico/chat.html",
        {
            "maquina": maquina,
            "sesion": sesion,
            "mensajes": mensajes,
        }
    )

@requiere_roles(["tecnico"])
def enviar_mensaje_lozai(request, maquina_id):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Método no permitido."},
            status=405
        )

    maquina, usuario, sesion = obtener_contexto_chat(
        request,
        maquina_id
    )

    mensaje = request.POST.get("mensaje", "").strip()

    if not mensaje:
        return JsonResponse(
            {"error": "El mensaje está vacío."},
            status=400
        )

    mensaje_tecnico = MensajeSesion.objects.create(
        sesion=sesion,
        emisor="tecnico",
        contenido=mensaje
    )

    try:
        service = LozAIService()
        respuesta = service.responder(
            maquina,
            mensaje
        )

    except Exception:
        respuesta = (
            "LozAI no pudo responder en este momento."
        )

    mensaje_lozai = MensajeSesion.objects.create(
        sesion=sesion,
        emisor="lozai",
        contenido=respuesta
    )

    return JsonResponse({
    "respuesta": mensaje_lozai.contenido,
    "fecha": mensaje_lozai.fecha.strftime(
        "%d/%m/%Y %H:%M"
    )
})