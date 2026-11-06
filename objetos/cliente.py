from datetime import date


class Cliente:
    def __init__(self, dni, nombre, apellido, fecha_nacimiento, telefono, email):
        self.__dni = dni
        self.__nombre = nombre
        self.__apellido = apellido
        self.__fecha_nacimiento = fecha_nacimiento  # objeto date
        self.telefono = telefono   # pasa por el setter
        self.email = email         # pasa por el setter (valida el "@")

    @property
    def dni(self):
        return self.__dni

    @property
    def nombre(self):
        return self.__nombre

    @property
    def apellido(self):
        return self.__apellido

    @property
    def fecha_nacimiento(self):
        return self.__fecha_nacimiento

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        self.__telefono = valor

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        Cliente.validar_email(valor)
        self.__email = valor

    @staticmethod
    def validar_email(valor):
        """Lanza ValueError si el email no es válido (vacío se permite: es opcional)."""
        if valor and "@" not in valor:
            raise ValueError("Email inválido")

    @property
    def edad(self):
        hoy = date.today()
        edad = hoy.year - self.__fecha_nacimiento.year
        if (hoy.month, hoy.day) < (self.__fecha_nacimiento.month, self.__fecha_nacimiento.day):
            edad -= 1
        return edad

    def verDatos(self):
        print("DNI:", self.__dni)
        print("Nombre:", self.__nombre, self.__apellido)
        print("Fecha de nacimiento:", self.__fecha_nacimiento.strftime("%d/%m/%Y"), f"({self.edad} años)")
        print("Teléfono:", self.__telefono)
        print("Email:", self.__email)

    def __str__(self):
        return f"{self.__dni} - {self.__apellido}, {self.__nombre} ({self.edad} años)"
