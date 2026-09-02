"""
ensamblador.py — El ÚNICO punto del sistema que decide qué motor se usa.

Los controladores llaman a `crear_servicio_proyecto()` y reciben algo que cumple
la interfaz del servicio. No saben —ni tienen por qué saber— qué repositorio
hay detrás.

Hoy hay un solo motor. El día que entre un segundo, este archivo es el único
que cambia: esa es toda la gracia de tener la construcción en un solo sitio.
"""

import os

from repositorios.repositorio_proyecto_postgresql import RepositorioProyectoPostgreSQL
from servicios.abstracciones.i_servicio_proyecto import IServicioProyecto
from servicios.servicio_proyecto import ServicioProyecto


def _cadena_conexion() -> str:
    cadena = os.environ.get("DB_POSTGRES")
    if not cadena:
        raise RuntimeError(
            "Falta la variable de entorno DB_POSTGRES con la cadena de conexión.")
    return cadena


def crear_servicio_proyecto() -> IServicioProyecto:
    """Arma el servicio con su repositorio. Construirlo NO abre conexiones."""
    return ServicioProyecto(RepositorioProyectoPostgreSQL(_cadena_conexion()))
