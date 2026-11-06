from datos.db_config import conectar
from objetos.siniestro import Siniestro


def guardarSiniestro(siniestro, pNumeroPoliza):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO siniestros (numero_poliza, fecha, descripcion, monto_reclamado, id_estado) "
            "VALUES (%s,%s,%s,%s,(SELECT id FROM siniestro_estado WHERE nombre = %s))",
            (pNumeroPoliza, siniestro.fecha, siniestro.descripcion,
             siniestro.monto_reclamado, siniestro.estado))
        conn.commit()
        numero = cursor.lastrowid
    finally:
        cursor.close()
        conn.close()
    return numero


def traerSiniestrosDePoliza(pNumeroPoliza):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT s.numero, s.fecha, s.descripcion, s.monto_reclamado, e.nombre AS estado "
            "FROM siniestros s JOIN siniestro_estado e ON e.id = s.id_estado "
            "WHERE s.numero_poliza = %s ORDER BY s.numero", (pNumeroPoliza,))
        filas = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return [Siniestro(f["numero"], f["fecha"], f["descripcion"],
                      float(f["monto_reclamado"]), f["estado"]) for f in filas]


def actualizarEstadoSiniestro(siniestro):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE siniestros SET id_estado = (SELECT id FROM siniestro_estado WHERE nombre = %s) "
                       "WHERE numero = %s",
                       (siniestro.estado, siniestro.numero))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
