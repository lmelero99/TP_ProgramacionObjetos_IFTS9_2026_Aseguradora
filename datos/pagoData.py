from datos.db_config import conectar
from objetos.pago import Pago


def guardarPago(pago, pNumeroPoliza):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pagos (numero_poliza, fecha, monto, periodo) VALUES (%s,%s,%s,%s)",
            (pNumeroPoliza, pago.fecha, pago.monto, pago.periodo))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def existePago(pNumeroPoliza, pPeriodo):
    """True si ya se pagó ese período para esa póliza."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM pagos WHERE numero_poliza = %s AND periodo = %s",
                       (pNumeroPoliza, pPeriodo))
        fila = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
    return fila is not None


def traerPagosDePoliza(pNumeroPoliza):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM pagos WHERE numero_poliza = %s ORDER BY periodo",
                       (pNumeroPoliza,))
        filas = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return [Pago(f["fecha"], float(f["monto"]), f["periodo"]) for f in filas]
