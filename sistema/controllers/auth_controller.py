
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import (
    make_password,
    check_password,
    identify_hasher,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.crypto import constant_time_compare

from sistema.models import Usuario


def verificar_password(usuario, password):
    try:
        identify_hasher(usuario.password)
        password_con_hash = True
    except ValueError:
        password_con_hash = False

    if password_con_hash:
        return check_password(password, usuario.password)

    if constant_time_compare(password, usuario.password):
        usuario.password = make_password(password)
        usuario.save(update_fields=["password"])
        return True

    return False


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        usuario = Usuario.objects.filter(
            email__iexact=email,
            activo=True
        ).first()

        if usuario and verificar_password(usuario, password):
            request.session.flush()

            request.session["usuario_id"] = usuario.id
            request.session["usuario_nombre"] = usuario.nombre
            request.session["usuario_rol"] = usuario.role

            return redirect("dashboard")

        return render(request, "login.html", {
            "error": "Email o contraseña incorrectos."
        })

    return render(request, "login.html")


def logout_view(request):
    request.session.flush()
    return redirect("login")


def register_view(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirmar = request.POST.get("confirmar_password", "")

        if not all([nombre, email, password, confirmar]):
            return render(request, "register.html", {
                "error": "Todos los campos son obligatorios."
            })

        if password != confirmar:
            return render(request, "register.html", {
                "error": "Las contraseñas no coinciden."
            })

        try:
            validate_email(email)
            validate_password(password)
        except ValidationError as error:
            return render(request, "register.html", {
                "error": " ".join(error.messages)
            })

        if Usuario.objects.filter(email__iexact=email).exists():
            return render(request, "register.html", {
                "error": "Ya existe un usuario con ese correo."
            })

        Usuario.objects.create(
            nombre=nombre,
            email=email,
            password=make_password(password),
            role="usuario",
            activo=True
        )

        return redirect("login")

    return render(request, "register.html")
