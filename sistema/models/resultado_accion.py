from django.db import models
from .solicitud import Solicitud


class ResultadoAccion(models.Model):
    solicitud = models.ForeignKey(Solicitud,on_delete=models.CASCADE)

    nombre_accion = models.CharField(max_length=100)
    exito = models.BooleanField(default=True)
    detalle = models.TextField()
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_accion} - {'OK' if self.exito else 'ERROR'}"

    class Meta:
        db_table = 'resultado_accion'