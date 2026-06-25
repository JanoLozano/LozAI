from django.db import models
from .sesion import Sesion

class MensajeSesion(models.Model):
    EMISORES = [
        ('tecnico', 'Técnico'),
        ('lozai', 'LozAI'),
    ]

    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE)
    emisor = models.CharField(max_length=20, choices=EMISORES)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.emisor} - Sesion {self.sesion.id}"

    class Meta:
        db_table = 'mensaje_sesion'