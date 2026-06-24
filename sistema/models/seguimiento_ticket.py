from django.db import models
from .solicitud import Solicitud
from .usuario import Usuario

class SeguimientoTicket(models.Model):
    ticket = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    comentario = models.TextField()
    estado_anterior = models.CharField(max_length=20, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=20, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Seguimiento Ticket {self.ticket.id}"

    class Meta:
        db_table = 'seguimiento_ticket'