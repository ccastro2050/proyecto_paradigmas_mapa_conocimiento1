"""
app.py — La capa de PRESENTACIÓN del sistema.

Estas son las vistas: reciben lo que el usuario hizo en el navegador, se lo
piden a `cliente_api`, y eligen qué plantilla mostrar. Nada más.

Las cuatro reglas de este archivo:

1. **No habla con la base de datos.** Ni siquiera sabe que existe PostgreSQL.
   Todo lo pide por HTTP a la API.
2. **No valida negocio.** Si un dato está mal, lo dice la API y aquí solo se
   muestra. Duplicar la regla en el front es tener dos dueños de la misma
   verdad.
3. **No importa nada de la API**, aunque las dos estén en Python y estén una
   al lado de la otra en el disco. Lo único que comparten es el JSON.
4. **No le habla al usuario en jerga.** Ni verbos, ni códigos de estado, ni
   nombres de tabla en la pantalla.

======================================================================
UNA PANTALLA POR TABLA, CON SU RUTA PROPIA
======================================================================

`/proyectos` — no `/tabla/<nombre>`. Una dirección con un hueco no es una
dirección de nada: un menú se arma con rutas que existen, y un marcador del
navegador apunta a una página, no a un molde.
"""

import os

from flask import Flask, flash, redirect, render_template, request, url_for

import cliente_api

app = Flask(__name__)

# `flash` guarda los avisos en la sesión, y la sesión va firmada: sin clave,
# Flask no arranca. En un proyecto real esto vive fuera de git.
app.secret_key = os.environ.get("CLAVE_SESION", "Paradigmas123!Sesion")

PUERTO = int(os.environ.get("PUERTO", 8079))


def _avisar(errores) -> None:
    """Cada error de la API se muestra como un aviso rojo, uno por línea."""
    for mensaje in errores:
        flash(mensaje, "error")


def _entero(texto: str):
    """El texto convertido a entero si lo es; si no, el texto tal cual.

    Parece una validación del lado del cliente, y hay que ser preciso porque
    no lo es. Un formulario HTML **solo produce texto**: el «12» que la
    persona escribió llega como "12". El contrato pide un número, y un número
    entre comillas haría que la API lo rechazara **siendo correcto**.

    Esto ajusta la FORMA del dato, que es trabajo del front, y no juzga su
    VALOR, que es trabajo de la API: si alguien escribió «doce», eso viaja
    como «doce» y la API responde 422.
    """
    texto = (texto or "").strip()
    if texto == "":
        return ""
    try:
        return int(texto)
    except ValueError:
        return texto


def _decimal(texto: str):
    """Lo mismo que `_entero`, para los números con decimales."""
    texto = (texto or "").strip()
    if texto == "":
        return ""
    try:
        return float(texto)
    except ValueError:
        return texto


def _si_lleno(cuerpo: dict, campo: str, valor) -> None:
    """Mete el campo SOLO si la persona escribió algo.

    Es la mitad del contraste entre los dos botones de guardar: lo que no se
    diligencia **no viaja**, y la API deja ese campo como estaba.
    """
    if valor not in ("", None):
        cuerpo[campo] = valor


# ======================================================================
# EL INICIO
# ======================================================================


@app.route("/")
def inicio():
    return render_template("inicio.html")


# ======================================================================
# PROYECTOS
# ======================================================================


@app.route("/proyectos")
def listar_proyectos():
    ok, filas, errores = cliente_api.listar_proyectos()
    if not ok:
        _avisar(errores)
    # Aun con error se pinta la pantalla: el usuario ve el aviso DENTRO de la
    # aplicación, no una página de error del servidor.
    return render_template("proyectos/lista.html", filas=filas)


@app.route("/proyectos/nuevo", methods=["GET", "POST"])
def crear_proyecto():
    if request.method == "GET":
        return render_template("proyectos/formulario.html", ficha=None, editando=False)

    cuerpo = _cuerpo_completo(con_llave=True)
    ok, errores = cliente_api.crear_proyecto(cuerpo)
    if ok:
        flash("Se agregó la ficha.", "exito")
        return redirect(url_for("listar_proyectos"))

    # Se devuelve el formulario CON lo que la persona había escrito: perder lo
    # digitado por un error de validación es castigarla dos veces.
    _avisar(errores)
    return render_template("proyectos/formulario.html", ficha=cuerpo, editando=False)


@app.route("/proyectos/<int:id>/editar", methods=["GET", "POST"])
def editar_proyecto(id):
    if request.method == "GET":
        ok, ficha, errores = cliente_api.obtener_proyecto(id)
        if not ok:
            _avisar(errores)
            return redirect(url_for("listar_proyectos"))
        return render_template("proyectos/formulario.html", ficha=ficha, editando=True)

    # ==================================================================
    # QUÉ BOTÓN SE OPRIMIÓ DECIDE QUÉ SE ENVÍA.
    # La diferencia NO está en un `if` de negocio: está en el CUERPO de la
    # petición. Uno manda un reemplazo completo y el otro solo lo llenado.
    # ==================================================================
    if request.form.get("verbo") == "completa":
        ok, errores = cliente_api.reemplazar_proyecto(id, _cuerpo_completo())
    else:
        ok, errores = cliente_api.actualizar_proyecto(id, _cuerpo_parcial())

    if ok:
        flash("Se guardaron los cambios.", "exito")
        return redirect(url_for("listar_proyectos"))

    _avisar(errores)
    ficha = dict(request.form)
    ficha["id"] = id
    return render_template("proyectos/formulario.html", ficha=ficha, editando=True)


@app.route("/proyectos/<int:id>/eliminar", methods=["POST"])
def eliminar_proyecto(id):
    """Se exige POST a propósito: un enlace GET que borra lo puede disparar
    el navegador solo, al precargar la página."""
    ok, errores = cliente_api.eliminar_proyecto(id)
    if ok:
        flash("Se retiró la ficha.", "exito")
    else:
        _avisar(errores)
    return redirect(url_for("listar_proyectos"))


# ======================================================================
# Los dos armadores del cuerpo
# ======================================================================


def _cuerpo_completo(con_llave: bool = False) -> dict:
    """Todos los campos, vayan llenos o no. Lo usan POST y PUT.

    Por eso un campo obligatorio en blanco se rechaza: viaja vacío, y la API
    dice que no cumple.
    """
    cuerpo = {
        "titulo": request.form.get("titulo", "").strip(),
        "resumen": request.form.get("resumen", "").strip(),
        "presupuesto": _decimal(request.form.get("presupuesto", "")),
        "tipo_financiacion": request.form.get("tipo_financiacion", "").strip(),
        "tipo_fondos": request.form.get("tipo_fondos", "").strip(),
        "fecha_inicio": request.form.get("fecha_inicio", "").strip(),
        "fecha_fin": request.form.get("fecha_fin", "").strip(),
    }

    # Los campos opcionales viajan como None cuando quedan en
    # blanco: «vacío» y «no aplica» son la misma cosa para ellos,
    # y un "" haría que Pydantic los rechazara.
    if not cuerpo["fecha_fin"]:
        cuerpo["fecha_fin"] = None

    if con_llave:
        cuerpo["id"] = _entero(request.form.get("id", ""))
    return cuerpo


def _cuerpo_parcial() -> dict:
    """Solo lo diligenciado. Lo usa PATCH.

    El mismo formulario a medio llenar que el reemplazo rechaza, aquí
    funciona — y lo que no se envía, la API lo deja como estaba.
    """
    cuerpo: dict = {}
    _si_lleno(cuerpo, "titulo", request.form.get("titulo", "").strip())
    _si_lleno(cuerpo, "resumen", request.form.get("resumen", "").strip())
    _si_lleno(cuerpo, "presupuesto", _decimal(request.form.get("presupuesto", "")))
    _si_lleno(cuerpo, "tipo_financiacion", request.form.get("tipo_financiacion", "").strip())
    _si_lleno(cuerpo, "tipo_fondos", request.form.get("tipo_fondos", "").strip())
    _si_lleno(cuerpo, "fecha_inicio", request.form.get("fecha_inicio", "").strip())
    _si_lleno(cuerpo, "fecha_fin", request.form.get("fecha_fin", "").strip())
    return cuerpo


# ======================================================================
# La pantalla de «esa página no existe»
# ======================================================================


@app.errorhandler(404)
def no_encontrada(_error):
    """Con el marco de la aplicación puesto, no una página en blanco."""
    return render_template("no_encontrada.html"), 404


if __name__ == "__main__":
    # host="0.0.0.0" para que se pueda entrar desde fuera del contenedor.
    app.run(host="0.0.0.0", port=PUERTO, debug=True)
