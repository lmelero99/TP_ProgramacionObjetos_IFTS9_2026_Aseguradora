import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import re
from datetime import date, datetime, timedelta
import mysql.connector
from objetos.cliente import Cliente
from objetos.poliza import Poliza, PolizaAuto, PolizaHogar, PolizaVida
from objetos.siniestro import Siniestro
from objetos.pago import Pago
from datos.clienteData import (guardarCliente, traerClientes, traerCliente,
                               modificarCliente, borrarCliente)
from datos.polizaData import (guardarPoliza, traerPolizasDeCliente, traerPoliza,
                              actualizarEstadoPoliza)
from datos.siniestroData import (guardarSiniestro, traerSiniestrosDePoliza,
                                 actualizarEstadoSiniestro)
from datos.pagoData import guardarPago, traerPagosDePoliza, existePago

# Máximo que entra en una columna DECIMAL(14,2)
MONTO_MAXIMO = 999_999_999_999.99


# ---------------------------------------------------------------
# Funciones auxiliares para pedir datos.
# Todas repiten la pregunta hasta que el dato ingresado sea válido.
# ---------------------------------------------------------------
def pedirEntero(mensaje, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(mensaje))
        except ValueError:
            print("Ingrese un número entero válido.")
            continue
        if minimo is not None and valor < minimo:
            print(f"El valor debe ser mayor o igual a {minimo}.")
        elif maximo is not None and valor > maximo:
            print(f"El valor debe ser menor o igual a {maximo}.")
        else:
            return valor


def pedirDecimal(mensaje):
    """Pide un monto mayor a cero que entre en la base de datos."""
    while True:
        try:
            valor = float(input(mensaje).replace(",", "."))
        except ValueError:
            print("Ingrese un número válido.")
            continue
        if not math.isfinite(valor) or valor <= 0:
            print("El monto debe ser un número mayor a cero.")
        elif valor > MONTO_MAXIMO:
            print(f"El monto no puede superar ${MONTO_MAXIMO:,.2f}.")
        else:
            return round(valor, 2)


def pedirTexto(mensaje, maximo, obligatorio=True):
    """Pide un texto sin espacios sobrantes y que entre en la columna de la BD."""
    while True:
        valor = input(mensaje).strip()
        if obligatorio and not valor:
            print("Este dato es obligatorio.")
        elif len(valor) > maximo:
            print(f"Máximo {maximo} caracteres.")
        else:
            return valor


def pedirFecha(mensaje, minimo=None, maximo=None):
    while True:
        try:
            valor = datetime.strptime(input(mensaje + " (dd/mm/aaaa): ").strip(), "%d/%m/%Y").date()
        except ValueError:
            print("Fecha inválida. Use el formato dd/mm/aaaa.")
            continue
        if minimo is not None and valor < minimo:
            print(f"La fecha debe ser igual o posterior al {minimo.strftime('%d/%m/%Y')}.")
        elif maximo is not None and valor > maximo:
            print(f"La fecha debe ser igual o anterior al {maximo.strftime('%d/%m/%Y')}.")
        else:
            return valor


def pedirEmail(mensaje):
    """Pide un email opcional: puede quedar vacío, pero si se escribe tiene que ser válido."""
    while True:
        valor = pedirTexto(mensaje, 80, obligatorio=False)
        try:
            Cliente.validar_email(valor)   # la misma regla que usa la clase Cliente
            return valor
        except ValueError as error:
            print("Error:", error)


def pedirSiNo(mensaje):
    while True:
        valor = input(mensaje + " (s/n): ").strip().lower()
        if valor in ("s", "n"):
            return valor == "s"
        print("Responda 's' o 'n'.")


def pedirCliente():
    """Pide un DNI hasta encontrar el cliente. Con Enter vacío se cancela y devuelve None."""
    while True:
        dni = input("Ingrese el DNI del cliente (Enter para volver): ").strip()
        if not dni:
            return None
        cli = traerCliente(dni)
        if cli is not None:
            return cli
        print("No existe un cliente con ese DNI.")


def pedirPoliza(validar=None):
    """Pide un número hasta encontrar una póliza válida. Con Enter vacío se cancela y devuelve None.
    validar(pol), si se indica, devuelve un mensaje de error o None si la póliza sirve."""
    while True:
        texto = input("Ingrese el número de póliza (Enter para volver): ").strip()
        if not texto:
            return None
        try:
            numero = int(texto)
        except ValueError:
            print("Ingrese un número entero válido.")
            continue
        pol = traerPoliza(numero)
        if pol is None:
            print("No existe una póliza con ese número.")
            continue
        error = validar(pol) if validar else None
        if error:
            print("Error:", error)
        else:
            return pol


def polizaVigente(pol):
    return None if pol.esta_vigente() else "la póliza no está vigente."


def polizaNoCancelada(pol):
    return "la póliza ya estaba cancelada." if pol.estado == Poliza.CANCELADA else None


# ---------------------------------------------------------------
# CLIENTES
# ---------------------------------------------------------------
def altaCliente():
    while True:
        dni = pedirTexto("DNI: ", 10)
        if traerCliente(dni) is None:
            break
        print("Ya existe un cliente con ese DNI.")
    nomb = pedirTexto("Nombre: ", 50)
    apel = pedirTexto("Apellido: ", 50)
    fnac = pedirFecha("Fecha de nacimiento", maximo=date.today())
    tel = pedirTexto("Teléfono: ", 20, obligatorio=False)
    mail = pedirEmail("Email: ")
    guardarCliente(Cliente(dni, nomb, apel, fnac, tel, mail))
    print("Cliente guardado !!!")


def menuClientes():
    while True:
        print("\n--- CLIENTES ---")
        print("1. Crear cliente")
        print("2. Ver clientes")
        print("3. Consultar cliente")
        print("4. Modificar cliente (teléfono y email)")
        print("5. Borrar cliente")
        print("0. Volver")
        opcion = pedirEntero("Ingrese una opción: ", 0, 5)

        if opcion == 1:
            altaCliente()
        elif opcion == 2:
            clientes = traerClientes()
            print("\nLista de clientes:")
            for cli in clientes:
                print(cli)
            if not clientes:
                print("(no hay clientes cargados)")
        elif opcion == 3:
            cli = pedirCliente()
            if cli:
                cli.verDatos()
                polizas = traerPolizasDeCliente(cli.dni)
                print(f"Pólizas contratadas: {len(polizas)}")
        elif opcion == 4:
            cli = pedirCliente()
            if cli:
                # Enter vacío deja el valor actual
                cli.telefono = pedirTexto(f"Nuevo teléfono [{cli.telefono}]: ", 20,
                                          obligatorio=False) or cli.telefono
                cli.email = pedirEmail(f"Nuevo email [{cli.email}]: ") or cli.email
                modificarCliente(cli)
                print("Cliente modificado !!!")
                cli.verDatos()
        elif opcion == 5:
            cli = pedirCliente()
            if cli and pedirSiNo(f"¿Borrar a {cli.apellido}, {cli.nombre}?"):
                try:
                    borrarCliente(cli.dni)
                    print("Cliente borrado !!!")
                except ValueError as error:
                    print("Error:", error)
        else:
            break


# ---------------------------------------------------------------
# POLIZAS
# ---------------------------------------------------------------
def contratarPoliza():
    cli = pedirCliente()
    if cli is None:
        return
    print("Tipo de póliza: 1. Auto  2. Hogar  3. Vida")
    tipo = pedirEntero("Ingrese el tipo: ", 1, 3)
    inicio = pedirFecha("Fecha de inicio")
    fin = pedirFecha("Fecha de fin", minimo=inicio + timedelta(days=1))
    suma = pedirDecimal("Suma asegurada: ")

    if tipo == 1:
        patente = pedirTexto("Patente: ", 10).upper()
        marca = pedirTexto("Marca: ", 30)
        modelo = pedirTexto("Modelo: ", 30)
        anio = pedirEntero("Año: ", 1900, date.today().year + 1)
        pol = PolizaAuto(None, inicio, fin, suma, patente, marca, modelo, anio)
    elif tipo == 2:
        direccion = pedirTexto("Dirección: ", 100)
        metros = pedirEntero("Metros cuadrados: ", 1, 100_000)
        pol = PolizaHogar(None, inicio, fin, suma, direccion, metros)
    else:
        beneficiario = pedirTexto("Beneficiario: ", 80)
        pol = PolizaVida(None, inicio, fin, suma, beneficiario, cli.edad)  # edad calculada del cliente

    numero = guardarPoliza(pol, cli.dni)
    print(f"Póliza #{numero} contratada !!! Prima mensual: ${pol.calcular_prima():,.2f}")


def menuPolizas():
    while True:
        print("\n--- POLIZAS ---")
        print("1. Contratar póliza")
        print("2. Ver pólizas de un cliente")
        print("3. Cancelar póliza")
        print("0. Volver")
        opcion = pedirEntero("Ingrese una opción: ", 0, 3)

        if opcion == 1:
            contratarPoliza()
        elif opcion == 2:
            cli = pedirCliente()
            if cli:
                polizas = traerPolizasDeCliente(cli.dni)
                if not polizas:
                    print("El cliente no tiene pólizas.")
                for pol in polizas:
                    print()
                    pol.verDatos()   # polimorfismo: cada tipo muestra sus datos
        elif opcion == 3:
            pol = pedirPoliza(polizaNoCancelada)
            if pol:
                pol.cancelar()
                actualizarEstadoPoliza(pol)
                print("Póliza cancelada !!!")
        else:
            break


# ---------------------------------------------------------------
# SINIESTROS
# ---------------------------------------------------------------
def denunciarSiniestro():
    pol = pedirPoliza(polizaVigente)
    if pol is None:
        return
    desc = pedirTexto("Descripción: ", 200)
    while True:
        sin = Siniestro(None, date.today(), desc, pedirDecimal("Monto reclamado: "))
        try:
            pol.registrar_siniestro(sin)   # valida las reglas de negocio (ej: no superar la suma asegurada)
            break
        except ValueError as error:
            print("Error:", error)
    numero = guardarSiniestro(sin, pol.numero)
    print(f"Siniestro #{numero} denunciado !!!")


def resolverSiniestro():
    pol = pedirPoliza()
    if pol is None:
        return
    siniestros = traerSiniestrosDePoliza(pol.numero)
    abiertos = {s.numero: s for s in siniestros if s.estado == Siniestro.ABIERTO}
    if not abiertos:
        print("La póliza no tiene siniestros abiertos.")
        return
    for sin in siniestros:
        print(sin)
    while True:
        numero = pedirEntero("Número de siniestro a resolver: ")
        if numero in abiertos:
            break
        if any(s.numero == numero for s in siniestros):
            print("El siniestro ya fue resuelto.")
        else:
            print("Ese siniestro no pertenece a la póliza.")
    sin = abiertos[numero]
    if pedirEntero("1. Aprobar  2. Rechazar: ", 1, 2) == 1:
        sin.aprobar()
        actualizarEstadoSiniestro(sin)
        pago = pol.calcular_indemnizacion(sin.monto_reclamado)
        print(f"Siniestro aprobado. Indemnización a pagar: ${pago:,.2f}")
    else:
        sin.rechazar()
        actualizarEstadoSiniestro(sin)
        print("Siniestro rechazado.")


def menuSiniestros():
    while True:
        print("\n--- SINIESTROS ---")
        print("1. Denunciar siniestro")
        print("2. Ver siniestros de una póliza")
        print("3. Aprobar / rechazar siniestro")
        print("0. Volver")
        opcion = pedirEntero("Ingrese una opción: ", 0, 3)

        if opcion == 1:
            denunciarSiniestro()
        elif opcion == 2:
            pol = pedirPoliza()
            if pol:
                siniestros = traerSiniestrosDePoliza(pol.numero)
                if not siniestros:
                    print("La póliza no tiene siniestros.")
                for sin in siniestros:
                    print(sin)
        elif opcion == 3:
            resolverSiniestro()
        else:
            break


# ---------------------------------------------------------------
# PAGOS
# ---------------------------------------------------------------
def registrarPago():
    pol = pedirPoliza(polizaVigente)
    if pol is None:
        return
    while True:
        periodo = input("Período que paga (aaaa-mm): ").strip()
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", periodo):
            print("Error: el período debe tener el formato aaaa-mm (ej: 2026-10).")
        elif existePago(pol.numero, periodo):
            print("Error: ese período ya fue pagado.")
        else:
            break
    cuota = round(pol.calcular_prima(), 2)
    guardarPago(Pago(date.today(), cuota, periodo), pol.numero)
    print(f"Pago registrado !!! Cuota: ${cuota:,.2f}")


def menuPagos():
    while True:
        print("\n--- PAGOS ---")
        print("1. Registrar pago de cuota")
        print("2. Ver pagos de una póliza")
        print("0. Volver")
        opcion = pedirEntero("Ingrese una opción: ", 0, 2)

        if opcion == 1:
            registrarPago()
        elif opcion == 2:
            pol = pedirPoliza()
            if pol:
                pagos = traerPagosDePoliza(pol.numero)
                if not pagos:
                    print("La póliza no tiene pagos.")
                for pago in pagos:
                    print(pago)
        else:
            break


# ---------------------------------------------------------------
# MENU PRINCIPAL
# ---------------------------------------------------------------
def menu():
    submenus = {1: menuClientes, 2: menuPolizas, 3: menuSiniestros, 4: menuPagos}
    while True:
        print("\n=== SISTEMA DE SEGUROS ===")
        print("1. Clientes")
        print("2. Pólizas")
        print("3. Siniestros")
        print("4. Pagos")
        print("0. Salir")
        opcion = pedirEntero("Ingrese una opción (0-4): ", 0, 4)

        if opcion == 0:
            print("\nSaliendo de la aplicación")
            break
        try:
            submenus[opcion]()
        except mysql.connector.Error as error:
            # Si se cae la BD (o no está levantada) avisamos en lugar de cerrar el programa
            print("Error de base de datos:", error)


if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo de la aplicación")
