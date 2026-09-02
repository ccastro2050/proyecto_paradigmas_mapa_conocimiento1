"""
Modelos Pydantic de proyecto — la FRONTERA DE ENTRADA de la API.

Aquí no hay ni un solo `if` de validación: se DECLARA la forma correcta de
los datos y Pydantic valida al construir el objeto. Un cuerpo inválido muere
en 422 antes de tocar el servicio o la base.

Hay UN modelo por semántica HTTP, y esa es la razón de que PUT y PATCH se
comporten distinto sin una línea que los compare.
"""

from datetime import date

from pydantic import BaseModel, Field


class Proyecto(BaseModel):
    """POST /api/proyecto — 7 campos obligatorios y 1 opcional."""

    """El código del proyecto."""
    id: int = Field(ge=1)
    titulo: str = Field(min_length=1, max_length=70)

    """El campo más largo de la tabla."""
    resumen: str = Field(min_length=1, max_length=256)

    """Un NÚMERO, no una cadena: si llega "mucho", es 422."""
    presupuesto: float = Field(ge=0)

    tipo_financiacion: str = Field(min_length=1, max_length=45)

    tipo_fondos: str = Field(min_length=1, max_length=45)

    """Fecha de verdad: la columna es DATE, no texto."""
    fecha_inicio: date


    """El ÚNICO opcional: un proyecto en curso todavía no terminó."""
    fecha_fin: date | None = None


class ProyectoReemplazo(BaseModel):
    """PUT /api/proyecto/{id} — reemplazo COMPLETO.

    Omitir un campo es 422, no "dejarlo como estaba": esa es la semántica
    de PUT. La llave no va aquí: identifica la fila y viaja en la ruta.
    """

    titulo: str = Field(min_length=1, max_length=70)

    """El campo más largo de la tabla."""
    resumen: str = Field(min_length=1, max_length=256)

    """Un NÚMERO, no una cadena: si llega "mucho", es 422."""
    presupuesto: float = Field(ge=0)

    tipo_financiacion: str = Field(min_length=1, max_length=45)

    tipo_fondos: str = Field(min_length=1, max_length=45)

    """Fecha de verdad: la columna es DATE, no texto."""
    fecha_inicio: date


    """El ÚNICO opcional: un proyecto en curso todavía no terminó."""
    fecha_fin: date | None = None


class ProyectoActualizar(BaseModel):
    """PATCH /api/proyecto/{id} — parcial: solo se modifican los enviados.

    El MISMO cuerpo que el modelo de arriba rechaza con 422, aquí es válido.
    Lo decide el tipo, no un if en el servicio.
    """

    titulo: str | None = Field(default=None, min_length=1, max_length=70)

    """El campo más largo de la tabla."""
    resumen: str | None = Field(default=None, min_length=1, max_length=256)

    """Un NÚMERO, no una cadena: si llega "mucho", es 422."""
    presupuesto: float | None = Field(default=None, ge=0)

    tipo_financiacion: str | None = Field(default=None, min_length=1, max_length=45)

    tipo_fondos: str | None = Field(default=None, min_length=1, max_length=45)

    """Fecha de verdad: la columna es DATE, no texto."""
    fecha_inicio: date | None = None

    """El ÚNICO opcional: un proyecto en curso todavía no terminó."""
    fecha_fin: date | None = None
