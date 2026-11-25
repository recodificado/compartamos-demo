from flask import Flask, render_template, request, redirect, url_for, abort, flash
import datos

app = Flask(__name__)
app.secret_key = "cambia-esto"


def campo(nombre, etiqueta, tipo="text"):
    return {"nombre": nombre, "etiqueta": etiqueta, "tipo": tipo}


# Entidades de datos reales de créditos (provenientes del Excel)
ENTIDADES = {
    "creditos": {
        "titulo": "Créditos", "icono": "bi-cash-coin",
        "campos": [
            campo("codigo_cuenta", "Cód. Cuenta", "number"),
            campo("nombre_unidad", "Cliente / Grupo"),
            campo("oficina", "Oficina"),
            campo("distrito", "Distrito"),
            campo("desembolso", "Desembolso", "number"),
            campo("saldo_capital", "Saldo Capital", "number"),
            campo("mto_cuota", "Monto Cuota", "number"),
            campo("asesor", "Asesor")
        ],
    }
}


@app.context_processor
def global_templates():
    return {"entidades": ENTIDADES}


@app.route("/")
def dashboard():
    est = datos.estadisticas()
    ultimos = datos.ultimos_creditos(10)
    return render_template("dashboard.html", est=est, ultimas=ultimos)


@app.route("/<entidad>")
def listar(entidad):
    if entidad not in ENTIDADES:
        abort(404)
    return render_template("entidad.html", clave=entidad, cfg=ENTIDADES[entidad],
                           filas=datos.listar(entidad))


@app.route("/<entidad>/guardar", methods=["POST"])
def guardar(entidad):
    if entidad not in ENTIDADES:
        abort(404)
    fila = {c["nombre"]: request.form.get(c["nombre"], "") for c in ENTIDADES[entidad]["campos"]}
    id_ = request.form.get("id")
    if id_:
        datos.editar(entidad, int(id_), fila)
        flash("Registro actualizado", "success")
    else:
        datos.agregar(entidad, fila)
        flash("Registro agregado", "success")
    return redirect(url_for("listar", entidad=entidad))


@app.route("/<entidad>/eliminar/<int:id_>", methods=["POST"])
def eliminar(entidad, id_):
    if entidad not in ENTIDADES:
        abort(404)
    datos.eliminar(entidad, id_)
    flash("Registro eliminado", "warning")
    return redirect(url_for("listar", entidad=entidad))


@app.errorhandler(404)
def no_encontrada(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
