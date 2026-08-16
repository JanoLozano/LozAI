import subprocess

from .tool import Tool

class PingTool(Tool):

    nombre = "ping"
    descripcion = "Comprueba la conectividad con una máquina."

    def ejecutar(self, maquina):
        try:
            comando = ["ping", "-n", "4", maquina.ip]

            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=10
            )

            salida = resultado.stdout.strip()

            if resultado.stderr:
                salida += f"\n\nErrores:\n{resultado.stderr.strip()}"

            return salida

        except subprocess.TimeoutExpired:
            return "Error: el comando ping superó el tiempo máximo de espera."

        except Exception as e:
            return f"Error al ejecutar el ping: {str(e)}"