from datos.db_config import conectar
from objetos.poliza import PolizaAuto, PolizaHogar, PolizaVida

# Trae los datos comunes, los nombres del tipo y del estado desde sus catálogos, y los datos
# de la subtabla que corresponda (las otras dos subtablas vienen en NULL por el LEFT JOIN).
_SELECT_POLIZA = (
    "SELECT p.numero, t.nombre AS tipo, p.fecha_inicio, p.fecha_fin, p.suma_asegurada, e.nombre AS estado, "
    "a.patente, a.marca, a.modelo, a.anio, "
    "h.direccion, h.metros_cuadrados, "
    "v.beneficiario, v.edad_asegurado "
    "FROM polizas p "
    "JOIN poliza_tipo t ON t.id = p.id_tipo "
    "JOIN poliza_estado e ON e.id = p.id_estado "
    "LEFT JOIN polizas_auto a ON a.numero = p.numero "
    "LEFT JOIN polizas_hogar h ON h.numero = p.numero "
    "LEFT JOIN polizas_vida v ON v.numero = p.numero "
)


def _armarPoliza(f):
    """Convierte una fila de la BD en el objeto de la clase hija que corresponda."""
    suma = float(f["suma_asegurada"])  # MySQL devuelve Decimal; lo pasamos a float
    if f["tipo"] == PolizaAuto.TIPO:
        return PolizaAuto(f["numero"], f["fecha_inicio"], f["fecha_fin"], suma,
                          f["patente"], f["marca"], f["modelo"], f["anio"], f["estado"])
    if f["tipo"] == PolizaHogar.TIPO:
        return PolizaHogar(f["numero"], f["fecha_inicio"], f["fecha_fin"], suma,
                           f["direccion"], f["metros_cuadrados"], f["estado"])
    if f["tipo"] == PolizaVida.TIPO:
        return PolizaVida(f["numero"], f["fecha_inicio"], f["fecha_fin"], suma,
                          f["beneficiario"], f["edad_asegurado"], f["estado"])
    raise ValueError(f"Tipo de póliza desconocido en la BD: {f['tipo']}")


def guardarPoliza(poliza, pDniCliente):
    """Inserta la póliza (tabla común + subtabla de su tipo) y devuelve el número asignado."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Los ids del tipo y del estado se buscan en sus catálogos por nombre
        cursor.execute(
            "INSERT INTO polizas (id_tipo, dni_cliente, fecha_inicio, fecha_fin, suma_asegurada, id_estado) "
            "VALUES ((SELECT id FROM poliza_tipo WHERE nombre = %s), %s, %s, %s, %s, "
            "(SELECT id FROM poliza_estado WHERE nombre = %s))",
            (poliza.TIPO, pDniCliente, poliza.fecha_inicio, poliza.fecha_fin,
             poliza.suma_asegurada, poliza.estado))
        numero = cursor.lastrowid

        if isinstance(poliza, PolizaAuto):
            cursor.execute(
                "INSERT INTO polizas_auto (numero, patente, marca, modelo, anio) VALUES (%s,%s,%s,%s,%s)",
                (numero, poliza.patente, poliza.marca, poliza.modelo, poliza.anio))
        elif isinstance(poliza, PolizaHogar):
            cursor.execute(
                "INSERT INTO polizas_hogar (numero, direccion, metros_cuadrados) VALUES (%s,%s,%s)",
                (numero, poliza.direccion, poliza.metros_cuadrados))
        elif isinstance(poliza, PolizaVida):
            cursor.execute(
                "INSERT INTO polizas_vida (numero, beneficiario, edad_asegurado) VALUES (%s,%s,%s)",
                (numero, poliza.beneficiario, poliza.edad_asegurado))

        conn.commit()    # las dos inserciones se confirman juntas
    except Exception:
        conn.rollback()  # si falla una, no queda una póliza a medias
        raise
    finally:
        cursor.close()
        conn.close()
    return numero


def traerPolizasDeCliente(pDni):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(_SELECT_POLIZA + "WHERE p.dni_cliente = %s ORDER BY p.numero", (pDni,))
        filas = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return [_armarPoliza(f) for f in filas]


def traerPoliza(pNumero):
    """Devuelve la póliza (del tipo correcto), o None si no existe."""
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(_SELECT_POLIZA + "WHERE p.numero = %s", (pNumero,))
        fila = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
    return _armarPoliza(fila) if fila else None


def actualizarEstadoPoliza(poliza):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE polizas SET id_estado = (SELECT id FROM poliza_estado WHERE nombre = %s) "
                       "WHERE numero = %s",
                       (poliza.estado, poliza.numero))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
