import os
import mysql.connector


def conectar():
    # Los datos se leen de variables de entorno; si no existen, se usan estos valores por defecto.
    # (Así no dejás tu contraseña escrita en el código si lo subís a GitHub.)
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "aseguradora")
    )
