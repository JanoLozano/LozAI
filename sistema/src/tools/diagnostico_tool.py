import platform
import psutil
from datetime import datetime
from .tool import Tool

class DiagnosticoTool:

    nombre = "diagnostico"
    descripcion = "Obtiene información de rendimiento del equipo."

    def ejecutar(self, maquina):
        try:
            memoria = psutil.virtual_memory()
            disco = psutil.disk_usage("/")
            bateria = psutil.sensors_battery()

            lineas = [
                f"Diagnóstico de rendimiento - {maquina.nombre}",
                "",
                "=== Datos registrados en el sistema ===",
                f"IP registrada: {maquina.ip}",
                f"Estado declarado: {maquina.estado}",
                f"Registro activo: {'sí' if maquina.activo else 'no'}",
                "",
                "=== Sistema operativo ===",
                f"Sistema: {platform.system()}",
                f"Versión: {platform.version()}",
                f"Arquitectura: {platform.machine()}",
                "",
                "=== CPU ===",
                f"Uso actual: {psutil.cpu_percent(interval=1)}%",
                f"Núcleos físicos: {psutil.cpu_count(logical=False)}",
                f"Núcleos lógicos: {psutil.cpu_count(logical=True)}",
                "",
                "=== Memoria RAM ===",
                f"Total: {self._gb(memoria.total)} GB",
                f"Disponible: {self._gb(memoria.available)} GB",
                f"Usada: {self._gb(memoria.used)} GB",
                f"Porcentaje de uso: {memoria.percent}%",
                "",
                "=== Disco principal ===",
                f"Total: {self._gb(disco.total)} GB",
                f"Usado: {self._gb(disco.used)} GB",
                f"Libre: {self._gb(disco.free)} GB",
                f"Porcentaje de uso: {disco.percent}%",
                "",
                "=== Procesos ===",
                f"Cantidad de procesos activos: {len(psutil.pids())}",
                "",
                "=== Batería ===",
                self._formatear_bateria(bateria),
                "",
                "=== Fecha del diagnóstico ===",
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            ]

            return "\n".join(lineas)

        except Exception as error:
            return f"Error al obtener diagnóstico de rendimiento: {error}"

    def _gb(self, bytes_valor):
        return round(bytes_valor / (1024 ** 3), 2)

    def _formatear_bateria(self, bateria):
        if bateria is None:
            return "No disponible o equipo sin batería."

        estado_carga = "conectada" if bateria.power_plugged else "desconectada"
        return f"Carga: {bateria.percent}% - Corriente: {estado_carga}"