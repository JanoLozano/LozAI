from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from sistema.models import Maquina, Sesion, MensajeSesion, Usuario
from sistema.src.lozai_service import LozAIService
from sistema.src.autorizacion import requiere_roles
from django.utils import timezone
from django.views.decorators.http import require_POST

def obtener_contexto_chat(request, maquina_id):
    maquina = get_object_or_404(
        Maquina,
        id=maquina_id,
        activo=True
    )

    usuario = get_object_or_404(
        Usuario,
        id=request.session.get("usuario_id"),
        activo=True
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

    maquina = get_object_or_404(
        Maquina,
        id=maquina_id
    )
    
    if not maquina.activo:
        messages.warning(
            request,
            f"La máquina '{maquina.nombre}' está deshabilitada. "
            "No es posible acceder a su chat."
        )
        return redirect("listar_maquinas")

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

    maquina = get_object_or_404(
        Maquina,
        id=maquina_id
    )

    if not maquina.activo:
        return JsonResponse(
            {"error": "La máquina está deshabilitada."},
            status=403
        )

    mensaje = request.POST.get("mensaje", "").strip()

    if not mensaje:
        return JsonResponse(
            {"error": "El mensaje está vacío."},
            status=400
        )

    maquina, usuario, sesion = obtener_contexto_chat(
        request,
        maquina_id
    )

    MensajeSesion.objects.create(
        sesion=sesion,
        emisor="tecnico",
        contenido=mensaje
    )

    try:
        service = LozAIService()
        respuesta = service.responder(maquina, mensaje)

        if not respuesta or not respuesta.strip():
            raise ValueError("Respuesta vacía de LozAI.")

    except Exception:
        return JsonResponse(
            {
                "error": "LozAI no está disponible en este momento. "
                        "Verificá que Ollama esté funcionando."
            },
            status=503
        )

    mensaje_lozai = MensajeSesion.objects.create(
        sesion=sesion,
        emisor="lozai",
        contenido=respuesta
    )

    return JsonResponse({
        "respuesta": mensaje_lozai.contenido,
        "fecha": mensaje_lozai.fecha.strftime("%d/%m/%Y %H:%M")
    })


@requiere_roles(["tecnico"])
@require_POST
def cerrar_sesion_lozai(request, maquina_id):
    maquina = get_object_or_404(
        Maquina,
        id=maquina_id
    )

    sesiones = Sesion.objects.filter(
        usuario_id=request.session.get("usuario_id"),
        maquina=maquina,
        fecha_fin__isnull=True
    )

    sesiones.update(
        fecha_fin=timezone.now()
    )

    messages.success(
        request,
        "La sesión de LozAI se cerró correctamente."
    )

    return redirect("listar_maquinas")