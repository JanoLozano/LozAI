from django.db import models
from .usuario import Usuario
from .maquina import Maquina

class Solicitud(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
    ]

    usuario = models.ForeignKey(
    Usuario,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, null=True, blank=True)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solicitud {self.id} - {self.usuario.nombre}"

    class Meta:
        db_table = 'solicitud'