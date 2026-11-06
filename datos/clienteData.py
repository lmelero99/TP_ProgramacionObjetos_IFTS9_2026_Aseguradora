import mysql.connector
from datos.db_config import conectar
from objetos.cliente import Cliente


def _armarCliente(f):
    return Cliente(f["dni"], f["nombre"], f["apellido"], f["fecha_nacimiento"],
                   f["telefono"], f["email"])


def guardarCliente(cliente):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO clientes (dni, nombre, apellido, fecha_nacimiento, telefono, email) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (cliente.dni, cliente.nombre, cliente.apellido, cliente.fecha_nacimiento,
             cliente.telefono, cliente.email))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def traerClientes():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM clientes ORDER BY apellido, nombre")
        filas = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return [_armarCliente(f) for f in filas]


def traerCliente(pDni):
    """Devuelve un Cliente, o None si no existe."""
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM clientes WHERE dni = %s", (pDni,))
        fila = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
    return _armarCliente(fila) if fila else None


def modificarCliente(cliente):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE clientes SET telefono = %s, email = %s WHERE dni = %s",
                       (cliente.telefono, cliente.email, cliente.dni))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def borrarCliente(pDni):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clientes WHERE dni = %s", (pDni,))
        conn.commit()
    except mysql.connector.IntegrityError:
        raise ValueError("No se puede borrar: el cliente tiene pólizas asociadas")
    finally:
        cursor.close()
        conn.close()
