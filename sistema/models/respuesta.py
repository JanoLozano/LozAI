from django.db import models
from .solicitud import Solicitud

class Respuesta(models.Model):
    solicitud = models.OneToOneField(Solicitud,on_delete=models.CASCADE)

    contenido = models.TextField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta {self.id} - Solicitud {self.solicitud.id}"

    class Meta:
        db_table = 'respuesta'