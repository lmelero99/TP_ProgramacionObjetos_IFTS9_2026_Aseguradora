from abc import ABC, abstractmethod
from datetime import date


class Poliza(ABC):
    VIGENTE = "vigente"
    VENCIDA = "vencida"
    CANCELADA = "cancelada"

    def __init__(self, numero, fecha_inicio, fecha_fin, suma_asegurada, estado=VIGENTE):
        self.__numero = numero          # None si todavía no se guardó en la BD
        self.__fecha_inicio = fecha_inicio
        self.__fecha_fin = fecha_fin
        self.__suma_asegurada = suma_asegurada
        self.__estado = estado

    @property
    def numero(self):
        return self.__numero

    @property
    def fecha_inicio(self):
        return self.__fecha_inicio

    @property
    def fecha_fin(self):
        return self.__fecha_fin

    @property
    def suma_asegurada(self):
        return self.__suma_asegurada

    @property
    def estado(self):
        return self.__estado

    def cancelar(self):
        if self.__estado == Poliza.CANCELADA:
            raise ValueError("La póliza ya estaba cancelada")
        self.__estado = Poliza.CANCELADA

    def estado_actual(self):
        """El estado guardado, pero marcando 'vencida' si ya pasó la fecha de fin."""
        if self.__estado == Poliza.VIGENTE and date.today() > self.__fecha_fin:
            return Poliza.VENCIDA
        return self.__estado

    def esta_vigente(self):
        hoy = date.today()
        return (self.__estado == Poliza.VIGENTE
                and self.__fecha_inicio <= hoy <= self.__fecha_fin)

    def registrar_siniestro(self, siniestro):
        """Valida las reglas de negocio antes de aceptar un siniestro."""
        if not self.esta_vigente():
            raise ValueError("No se puede denunciar un siniestro: la póliza no está vigente")
        if siniestro.monto_reclamado <= 0:
            raise ValueError("El monto reclamado debe ser mayor a cero")
        if siniestro.monto_reclamado > self.__suma_asegurada:
            raise ValueError("El monto reclamado supera la suma asegurada")

    @abstractmethod
    def calcular_prima(self):
        """Devuelve la cuota mensual."""

    @abstractmethod
    def calcular_indemnizacion(self, monto_reclamado):
        """Devuelve cuánto paga la compañía ante un reclamo."""

    def verDatos(self):
        print(f"Póliza #{self.__numero} ({self.TIPO}) - {self.estado_actual()}")
        print(f"Vigencia: {self.__fecha_inicio.strftime('%d/%m/%Y')} al {self.__fecha_fin.strftime('%d/%m/%Y')}")
        print(f"Suma asegurada: ${self.__suma_asegurada:,.2f}")
        print(f"Prima mensual: ${self.calcular_prima():,.2f}")


class PolizaAuto(Poliza):
    TIPO = "auto"
    FRANQUICIA = 0.10  # el cliente se hace cargo del 10%

    def __init__(self, numero, fecha_inicio, fecha_fin, suma_asegurada,
                 patente, marca, modelo, anio, estado=Poliza.VIGENTE):
        super().__init__(numero, fecha_inicio, fecha_fin, suma_asegurada, estado)
        self.__patente = patente
        self.__marca = marca
        self.__modelo = modelo
        self.__anio = anio

    @property
    def patente(self):
        return self.__patente

    @property
    def marca(self):
        return self.__marca

    @property
    def modelo(self):
        return self.__modelo

    @property
    def anio(self):
        return self.__anio

    def calcular_prima(self):
        antiguedad = max(0, date.today().year - self.__anio)  # un 0km del año que viene no resta
        return self.suma_asegurada * 0.01 + antiguedad * 500

    def calcular_indemnizacion(self, monto_reclamado):
        cubierto = min(monto_reclamado, self.suma_asegurada)
        return cubierto * (1 - PolizaAuto.FRANQUICIA)

    def verDatos(self):
        super().verDatos()
        print(f"Vehículo: {self.__marca} {self.__modelo} {self.__anio} - Patente {self.__patente}")


class PolizaHogar(Poliza):
    TIPO = "hogar"
    PRECIO_M2 = 800

    def __init__(self, numero, fecha_inicio, fecha_fin, suma_asegurada,
                 direccion, metros_cuadrados, estado=Poliza.VIGENTE):
        super().__init__(numero, fecha_inicio, fecha_fin, suma_asegurada, estado)
        self.__direccion = direccion
        self.__metros_cuadrados = metros_cuadrados

    @property
    def direccion(self):
        return self.__direccion

    @property
    def metros_cuadrados(self):
        return self.__metros_cuadrados

    def calcular_prima(self):
        return self.__metros_cuadrados * PolizaHogar.PRECIO_M2

    def calcular_indemnizacion(self, monto_reclamado):
        return min(monto_reclamado, self.suma_asegurada)

    def verDatos(self):
        super().verDatos()
        print(f"Inmueble: {self.__direccion} ({self.__metros_cuadrados} m²)")


class PolizaVida(Poliza):
    TIPO = "vida"

    def __init__(self, numero, fecha_inicio, fecha_fin, suma_asegurada,
                 beneficiario, edad_asegurado, estado=Poliza.VIGENTE):
        super().__init__(numero, fecha_inicio, fecha_fin, suma_asegurada, estado)
        self.__beneficiario = beneficiario
        self.__edad_asegurado = edad_asegurado

    @property
    def beneficiario(self):
        return self.__beneficiario

    @property
    def edad_asegurado(self):
        return self.__edad_asegurado

    def calcular_prima(self):
        return self.suma_asegurada * 0.001 * (self.__edad_asegurado / 10)

    def calcular_indemnizacion(self, monto_reclamado):
        return self.suma_asegurada  # paga la suma completa al beneficiario

    def verDatos(self):
        super().verDatos()
        print(f"Beneficiario: {self.__beneficiario} (asegurado de {self.__edad_asegurado} años)")
