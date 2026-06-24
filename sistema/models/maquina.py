from django.db import models

class Maquina(models.Model):
    ESTADOS = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
    ]
    nombre = models.CharField(max_length=100, unique=True)
    ip = models.GenericIPAddressField(unique=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activa')
    ultima_revision = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.ip}"
    
    class Meta:
        db_table = 'maquina'