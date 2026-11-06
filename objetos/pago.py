class Pago:
    def __init__(self, fecha, monto, periodo):
        self.__fecha = fecha
        self.__monto = monto
        self.__periodo = periodo  # ej: "2026-10"

    @property
    def fecha(self):
        return self.__fecha

    @property
    def monto(self):
        return self.__monto

    @property
    def periodo(self):
        return self.__periodo

    def __str__(self):
        return f"Período {self.__periodo} - ${self.__monto:,.2f} (pagado el {self.__fecha.strftime('%d/%m/%Y')})"
