class Siniestro:
    ABIERTO = "abierto"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"

    def __init__(self, numero, fecha, descripcion, monto_reclamado, estado=ABIERTO):
        self.__numero = numero          # None si todavía no se guardó en la BD
        self.__fecha = fecha
        self.__descripcion = descripcion
        self.__monto_reclamado = monto_reclamado
        self.__estado = estado

    @property
    def numero(self):
        return self.__numero

    @property
    def fecha(self):
        return self.__fecha

    @property
    def descripcion(self):
        return self.__descripcion

    @property
    def monto_reclamado(self):
        return self.__monto_reclamado

    @property
    def estado(self):
        return self.__estado

    def aprobar(self):
        self.__estado = Siniestro.APROBADO

    def rechazar(self):
        self.__estado = Siniestro.RECHAZADO

    def __str__(self):
        return (f"#{self.__numero} [{self.__estado}] {self.__fecha.strftime('%d/%m/%Y')} - "
                f"${self.__monto_reclamado:,.2f} - {self.__descripcion}")
