from django.db import models
from .solicitud import Solicitud

class Historial(models.Model):
    solicitud = models.ForeignKey(Solicitud,on_delete=models.CASCADE)
    accion_realizada = models.CharField(max_length=150)
    resultado = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Historial {self.id} - Solicitud {self.solicitud.id}"

    class Meta:
        db_table = 'historial'