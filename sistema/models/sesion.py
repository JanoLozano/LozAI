from django.db import models
from .usuario import Usuario
from .maquina import Maquina

class Sesion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, null=True, blank=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Sesion {self.id} - {self.usuario.nombre}"

    class Meta:
        db_table = 'sesion'