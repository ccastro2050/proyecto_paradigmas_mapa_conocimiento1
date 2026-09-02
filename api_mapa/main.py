"""
main.py — El arranque de la API del módulo Mapa de Conocimiento.

Arma la aplicación y registra el router. Nada más: la lógica vive en las
capas, no aquí.

Arranque:  uvicorn main:app --port 8031 --reload
Contratos: http://localhost:8031/docs
"""

from fastapi import FastAPI

from controllers.proyecto_controller import router as router_proyecto

app = FastAPI(
    title="API Mapa de Conocimiento",
    description="Módulo Mapa de Conocimiento — versión 1: el CRUD de proyecto.",
    version="v1",
)

app.include_router(router_proyecto)


@app.get("/")
async def diagnostico():
    """Responde sin tocar la base: sirve para saber si la API está viva."""
    return {"mensaje": "API Mapa de Conocimiento — módulo de proyecto",
            "version": "v1", "contratos": "/docs"}
