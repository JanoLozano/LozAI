from django.db import models

class Usuario(models.Model):
    ROLES = [
        ('admin', 'Administrador'),
        ('tecnico', 'Técnico'),
        ('usuario', 'Usuario'),
    ]

    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLES)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre