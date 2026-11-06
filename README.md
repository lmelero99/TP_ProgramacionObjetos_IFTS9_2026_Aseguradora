# Sistema de Seguros

Programa de consola en Python para administrar una aseguradora: clientes, pólizas (de auto, hogar y vida), siniestros y pagos de cuotas. Los datos se guardan en una base MySQL.

El objetivo del proyecto es aplicar los fundamentos de la Programación Orientada a Objetos (POO). Por eso, además de explicar cómo usarlo, este documento muestra **dónde aparece cada concepto de POO dentro del código**.

---

## 1. Cómo ponerlo en marcha

**Requisitos:** Python 3 y MySQL 8.

1. Instalar la librería de conexión a MySQL:
   ```powershell
   pip install -r requirements.txt
   ```
2. Crear la base de datos `aseguradora` con sus tablas y datos precargados (pide la contraseña de root):
   ```powershell
   & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -e "source script_bd.sql"
   ```
3. Indicar la contraseña de la base y ejecutar el programa:
   ```powershell
   $env:DB_PASSWORD = "tu_contraseña"
   python presentacion\app.py
   ```

La conexión se configura en `datos/db_config.py` con las variables de entorno `DB_HOST`, `DB_USER`, `DB_PASSWORD` y `DB_NAME`. Si no se definen, usa `localhost`, `root`, sin contraseña y `aseguradora`.

---

## 2. Qué hace el programa

El menú principal tiene cuatro secciones:

| Menú | Opciones |
|---|---|
| **Clientes** | Crear, listar, consultar, modificar teléfono y email, borrar (solo si no tiene pólizas) |
| **Pólizas** | Contratar una póliza de auto, hogar o vida; ver las pólizas de un cliente; cancelar una póliza |
| **Siniestros** | Denunciar un siniestro sobre una póliza vigente; ver los siniestros de una póliza; aprobarlos o rechazarlos (al aprobar se calcula la indemnización) |
| **Pagos** | Registrar el pago de la cuota mensual de un período; ver los pagos de una póliza |

Reglas principales:
- Solo se pueden denunciar siniestros y registrar pagos sobre pólizas **vigentes**: no canceladas y con la fecha de hoy dentro del período de vigencia.
- El monto reclamado en un siniestro no puede superar la suma asegurada.
- Cada período (`aaaa-mm`) se puede pagar una sola vez por póliza.
- Cada tipo de póliza calcula su cuota mensual (prima) y su indemnización de forma distinta.
- Si un dato ingresado no es válido, el programa lo vuelve a pedir. En los prompts que buscan un cliente o una póliza, Enter vacío vuelve al menú.

### Estructura del proyecto

```
aseguradora/
├── objetos/          Clases del dominio: Cliente, Poliza (y sus hijas), Siniestro, Pago
├── datos/            Acceso a la base de datos (guardar y traer objetos)
├── presentacion/     app.py: menús y pedido de datos por consola
├── script_bd.sql     Creación de la base de datos
├── diagrama_clases.mmd   Diagrama de clases UML (Mermaid)
└── requirements.txt
```

### Base de datos

| Tabla | Contenido |
|---|---|
| `clientes` | Datos de cada cliente |
| `poliza_tipo` | Catálogo precargado: auto, hogar, vida |
| `poliza_estado` | Catálogo precargado: vigente, cancelada |
| `polizas` | Datos comunes a todas las pólizas (con su tipo, estado y cliente) |
| `polizas_auto`, `polizas_hogar`, `polizas_vida` | Datos propios de cada tipo de póliza |
| `siniestro_estado` | Catálogo precargado: abierto, aprobado, rechazado |
| `siniestros` | Siniestros de cada póliza |
| `pagos` | Pagos de cuotas de cada póliza |

---

## 3. Conceptos de POO aplicados

### 3.1 Modelo y abstracción

Un **modelo** es una versión simplificada de una entidad del mundo real, construida mediante **abstracción**: se descartan las características que no son relevantes y se conservan las que sí lo son para el contexto.

Este programa es un modelo de una aseguradora. De un cliente real solo interesa lo necesario para asegurarlo: DNI, nombre, apellido, fecha de nacimiento, teléfono y email. Su dirección, su profesión o su estado civil quedan afuera porque no aportan nada en este contexto. Lo mismo pasa con un vehículo: de un auto solo se guardan patente, marca, modelo y año.

La abstracción también aparece al reconocer **similitudes**: una póliza de auto, una de hogar y una de vida son distintas, pero todas tienen un número, fechas de vigencia, una suma asegurada y un estado, y todas saben calcular una prima. Esa similitud se abstrae en el concepto general `Poliza`.

### 3.2 Clases, objetos e instancias

Una **clase** es el molde o plano con el que se construyen los objetos. Describe la estructura interna (variables de instancia) y el comportamiento (mensajes) que tendrán todas sus instancias. El programa define siete clases en `objetos/`: `Cliente`, `Poliza`, `PolizaAuto`, `PolizaHogar`, `PolizaVida`, `Siniestro` y `Pago`.

Un **objeto** es una **instancia** de una clase. Cada objeto tiene **estado**, un **comportamiento** bien definido e **identidad**. Por ejemplo, dos clientes distintos son dos instancias de `Cliente`: comparten la misma estructura y responden a los mismos mensajes, pero cada uno tiene **sus propios** valores de DNI, nombre, email, etc.

### 3.3 Instanciación

La **instanciación** es el mecanismo de creación de objetos a partir de su clase. Todas las instancias de una misma clase tienen la misma estructura interna y responden al mismo protocolo. En Python no se usa la palabra `new`: se instancia invocando a la clase. Al hacerlo se ejecuta `__init__`, que inicializa las variables de instancia.

```python
# presentacion/app.py — al contratar una póliza de auto
pol = PolizaAuto(None, inicio, fin, suma, patente, marca, modelo, anio)
```

Los objetos también se instancian a partir de los datos de la base. La función `_armarPoliza` (en `datos/polizaData.py`) decide qué clase instanciar según el tipo guardado:

```python
if f["tipo"] == PolizaAuto.TIPO:
    return PolizaAuto(f["numero"], f["fecha_inicio"], ...)
if f["tipo"] == PolizaHogar.TIPO:
    return PolizaHogar(f["numero"], f["fecha_inicio"], ...)
```

### 3.4 Estado interno y variables de instancia

El **estado interno** de un objeto está formado por sus **variables de instancia**, que lo acompañan durante todo su ciclo de vida y pueden cambiar con el tiempo. En `Siniestro`:

```python
def __init__(self, numero, fecha, descripcion, monto_reclamado, estado=ABIERTO):
    self.__numero = numero
    self.__fecha = fecha
    self.__descripcion = descripcion
    self.__monto_reclamado = monto_reclamado
    self.__estado = estado
```

El estado de un siniestro empieza en `"abierto"` y cambia cuando se le envía `aprobar()` o `rechazar()`. Pasa lo mismo que en el ejemplo de la cuenta bancaria, cuyo saldo cambia al depositar.

### 3.5 Encapsulamiento

El **encapsulamiento** separa lo **público** de un objeto (los mensajes que entiende, su **protocolo**) de lo **privado** (su estructura interna y la implementación de sus métodos). Así un cambio dentro de un objeto no se propaga por todo el sistema, y el **acoplamiento** entre las partes se mantiene bajo.

**Variables de instancia privadas.** Todas las variables de instancia se escriben con doble guion bajo (`self.__dni`, `self.__estado`, ...). Python las oculta: desde afuera de la clase no se puede acceder a ellas con ese nombre. La única forma de interactuar con el objeto es enviarle mensajes.

**El objeto decide qué publica.** `Cliente` publica mensajes para **consultar** su DNI, nombre, apellido y fecha de nacimiento, pero no para modificarlos. Solo teléfono y email tienen un mensaje para modificarlos, y ese mensaje controla el valor recibido:

```python
@property
def email(self):              # mensaje para consultar el email
    return self.__email

@email.setter
def email(self, valor):       # mensaje para modificarlo: valida antes de cambiar el estado
    Cliente.validar_email(valor)
    self.__email = valor
```

**El estado cambia solo a través del protocolo.** Nadie puede escribir directamente `estado = "cancelada"` en una póliza: hay que enviarle el mensaje `cancelar()`, y es la póliza la que decide si lo acepta.

```python
def cancelar(self):
    if self.__estado == Poliza.CANCELADA:
        raise ValueError("La póliza ya estaba cancelada")
    self.__estado = Poliza.CANCELADA
```

**La representación está sujeta a cambios.** Durante el desarrollo, la base de datos se reestructuró varias veces: se separaron las pólizas en subtablas por tipo y se crearon tablas de catálogo para tipos y estados. Ninguno de esos cambios obligó a modificar las clases de `objetos/`, porque el resto del programa trabaja con sus mensajes y no con su estructura interna.

### 3.6 Comportamiento, mensajes y métodos

El **comportamiento** de un objeto es el conjunto de **mensajes** a los que puede responder. Para pedirle algo a un objeto se le **envía un mensaje**, con la sintaxis `<objeto receptor>.<nombre de mensaje>(<parámetros>)`:

```python
# presentacion/app.py
pago = pol.calcular_indemnizacion(sin.monto_reclamado)
```

Acá se envían dos mensajes: primero `monto_reclamado` al siniestro `sin`, y con lo que devuelve, `calcular_indemnizacion` a la póliza `pol`.

El **método** es la implementación del mensaje: indica **cómo** lo resuelve el objeto. Un método puede hacer tres cosas, y las tres aparecen en el programa:

| Lo que hace un método | Ejemplo |
|---|---|
| Modificar el estado interno del objeto | `Siniestro.aprobar()` cambia `__estado` a `"aprobado"` |
| Colaborar con otros objetos enviándoles mensajes | `Poliza.registrar_siniestro(siniestro)` le envía `monto_reclamado` al siniestro y `esta_vigente()` a sí misma |
| Retornar un resultado | `PolizaHogar.calcular_prima()` devuelve `metros_cuadrados * PRECIO_M2` |

Python pertenece al grupo de lenguajes que, si un objeto no entiende un mensaje, responden con un **error en tiempo de ejecución**: por ejemplo, enviarle `calcular_prima()` a un `Cliente`.

### 3.7 Formas de conocimiento

Para que un objeto le envíe un mensaje a otro, primero lo tiene que conocer, es decir, poder nombrarlo. Las cuatro formas de conocimiento aparecen en `Poliza` y sus clases hijas:

| Forma | Qué es | Ejemplo en el código |
|---|---|---|
| **Interno**: variables de instancia | Lo que el objeto conoce durante toda su vida | `self.__fecha_fin` en `Poliza` |
| **Externo**: parámetros | Lo que recibe junto con el mensaje para resolverlo | `siniestro` en `registrar_siniestro(siniestro)`; `monto_reclamado` en `calcular_indemnizacion(monto_reclamado)` |
| **Temporal**: variables temporales | Nombres que existen solo mientras se ejecuta el método | `hoy` en `esta_vigente()`; `antiguedad` en `PolizaAuto.calcular_prima()`; `cubierto` en `PolizaAuto.calcular_indemnizacion()` |
| **Seudovariable** `this` | El objeto se nombra a sí mismo para enviarse mensajes | En Python se llama `self`: `self.esta_vigente()` dentro de `registrar_siniestro` |

```python
def esta_vigente(self):
    hoy = date.today()                       # variable temporal
    return (self.__estado == Poliza.VIGENTE  # variable de instancia
            and self.__fecha_inicio <= hoy <= self.__fecha_fin)
```

### 3.8 Identidad e igualdad

Todo objeto tiene **identidad**: solo es idéntico a sí mismo. **Identidad no es lo mismo que igualdad.**

Si se pide dos veces la póliza número 1 a la base (`traerPoliza(1)`), se obtienen **dos objetos distintos**, cada uno con su propia identidad, aunque los dos representen la misma póliza. Por eso el programa no distingue las pólizas, siniestros o clientes por el objeto en memoria, sino por un dato: el número de póliza, el número de siniestro o el DNI. Por ejemplo, al resolver un siniestro:

```python
if any(s.numero == numero for s in siniestros):
```

### 3.9 Generalización y herencia (relación es-un)

La **generalización** representa la relación **es-un**: una `PolizaAuto` **es una** `Poliza`, igual que `PolizaHogar` y `PolizaVida`.

```python
class PolizaAuto(Poliza):
class PolizaHogar(Poliza):
class PolizaVida(Poliza):
```

- **La clase hija hereda** las variables de instancia y las operaciones del padre. `cancelar()`, `esta_vigente()`, `estado_actual()` y `registrar_siniestro()` se escriben **una sola vez** en `Poliza` y las tres hijas las reutilizan. Es el **comportamiento común entre objetos** factorizado en un solo lugar.
- **La clase hija añade** sus propios atributos y operaciones: `PolizaAuto` agrega patente, marca, modelo y año; `PolizaHogar` agrega dirección y metros cuadrados; `PolizaVida` agrega beneficiario y edad del asegurado.
- **La clase hija redefine** operaciones del padre con la misma firma. Las tres redefinen `calcular_prima()`, `calcular_indemnizacion()` y `verDatos()`:

| Clase | `calcular_prima()` | `calcular_indemnizacion(monto)` |
|---|---|---|
| `PolizaAuto` | 1% de la suma asegurada + $500 por año de antigüedad del vehículo | Lo reclamado (hasta la suma asegurada) menos la franquicia del 10% |
| `PolizaHogar` | Metros cuadrados × $800 | Lo reclamado, hasta la suma asegurada |
| `PolizaVida` | Suma asegurada × 0,001 × (edad / 10) | La suma asegurada completa |

En `verDatos()`, cada hija reutiliza el método del padre (que muestra los datos comunes) y le agrega lo propio:

```python
def verDatos(self):          # en PolizaAuto
    super().verDatos()
    print(f"Vehículo: {self.__marca} {self.__modelo} {self.__anio} - Patente {self.__patente}")
```

Términos de UML que aplican a esta jerarquía:
- `Poliza` es la **clase raíz o clase base**: no tiene padres y tiene hijos.
- `PolizaAuto`, `PolizaHogar` y `PolizaVida` son **clases hija**: no tienen hijos.
- Cada hija tiene un único padre, así que usa **herencia simple**.
- En el programa nunca se instancia `Poliza` directamente: siempre se crea alguna de sus hijas.

### 3.10 Referencias polimórficas

La generalización indica que **los objetos hijos se pueden usar en cualquier lugar donde puede aparecer el padre**. En el programa, la variable `pol` puede referenciar durante la ejecución a una `PolizaAuto`, una `PolizaHogar` o una `PolizaVida`: es una **referencia polimórfica**. Quien le envía mensajes no necesita saber de qué clase concreta es:

```python
# presentacion/app.py — listar las pólizas de un cliente
for pol in polizas:
    pol.verDatos()      # cada póliza responde con el método de su propia clase
```

Al recibir un mensaje, el método se busca en la **clase del objeto receptor**. Esto pasa incluso cuando el objeto se envía un mensaje a sí mismo: `Poliza.verDatos()` ejecuta `self.calcular_prima()`, y ese mensaje se resuelve con el método de la clase hija que corresponda.

```python
print(f"Prima mensual: ${self.calcular_prima():,.2f}")   # en Poliza.verDatos()
```

### 3.11 Relaciones entre clases (asociación y composición)

Una **relación** es una conexión semántica entre objetos. Además de la generalización, el modelo tiene:

- **Asociación** `Cliente` — `Poliza`, con nombre *contrata*. Su **multiplicidad** es: un cliente contrata **0..\*** pólizas, y cada póliza pertenece a **exactamente 1** cliente.
- **Composición** `Poliza` ◆— `Siniestro` y `Poliza` ◆— `Pago` (relación **tiene-un**, todo/parte). Una póliza tiene 0..\* siniestros y 0..\* pagos. Es composición porque hay **exclusividad**: un siniestro o un pago pertenece a una sola póliza. También hay **dependencia**: no pueden existir sin su póliza (en la base, `numero_poliza` es obligatorio y referencia a la póliza).
- **Navegabilidad**: desde un cliente se llega a sus pólizas, y desde una póliza a sus siniestros y pagos. No se navega en sentido inverso: un siniestro no conoce a su póliza.

En el código, estas relaciones no se guardan como variables de instancia, sino que se resuelven con la capa de datos. Por ejemplo, `traerPolizasDeCliente(dni)` devuelve las pólizas de un cliente y `traerSiniestrosDePoliza(numero)` los siniestros de una póliza.

### 3.12 Atributos y operaciones: de clase, derivados, frozen y consultas

El diagrama de clases usa estas notaciones de UML, y todas tienen su correspondencia en el código:

- **Atributos de clase** (subrayados en UML; con `$` en Mermaid): son compartidos por todas las instancias de la clase. Por ejemplo, `Poliza.VIGENTE`, `Poliza.CANCELADA`, `Siniestro.ABIERTO`, `PolizaAuto.TIPO`, `PolizaAuto.FRANQUICIA` y `PolizaHogar.PRECIO_M2`. La franquicia del 10% es la misma para todas las pólizas de auto, así que no tiene sentido guardarla en cada instancia.
- **Operación de clase**: `Cliente.validar_email(valor)` se le envía a la clase, no a una instancia. Así, la regla del email se puede usar antes de crear el cliente (al pedir el dato por consola) y también dentro del objeto (al modificar el email).
- **Atributo derivado** (`/` en UML): `edad` en `Cliente` no se guarda en ningún lado. Se **deriva** de la fecha de nacimiento, igual que en el ejemplo del documento. Pasa lo mismo con el estado "vencida" de una póliza: no se guarda en la base, lo calcula `estado_actual()` comparando la fecha de fin con la de hoy.
- **Atributos frozen**: DNI, nombre, apellido y fecha de nacimiento de un cliente no se pueden modificar después de inicializar el objeto, porque la clase solo publica mensajes para consultarlos. Teléfono y email son **changeable**.
- **Operaciones isQuery**: `esta_vigente()`, `estado_actual()`, `calcular_prima()` y `calcular_indemnizacion()` no cambian ningún atributo: solo consultan y devuelven un resultado.

### 3.13 Visibilidad

En el diagrama de clases:
- **Privado (`-`)**: todas las variables de instancia. Solo se pueden usar dentro del objeto donde están definidas.
- **Público (`+`)**: los mensajes del protocolo. Cualquier objeto puede enviarlos.

Ni siquiera las clases hijas acceden a las variables privadas del padre. Por ejemplo, `PolizaAuto` no usa `__suma_asegurada` directamente: le envía el mensaje público `suma_asegurada` a sí misma.

```python
def calcular_prima(self):    # en PolizaAuto
    antiguedad = max(0, date.today().year - self.__anio)
    return self.suma_asegurada * 0.01 + antiguedad * 500
```

### 3.14 Responsabilidades

Cada clase tiene responsabilidades acotadas y bien definidas. Según el documento, eso hace que un objeto sea más fácil de reutilizar.

| Clase | Responsabilidades |
|---|---|
| `Cliente` | Conocer sus datos personales, calcular su edad y validar su email |
| `Poliza` | Conocer su vigencia y estado, cancelarse, decir si está vigente, validar si acepta un siniestro |
| `PolizaAuto` / `PolizaHogar` / `PolizaVida` | Calcular su prima y su indemnización según las reglas de su tipo |
| `Siniestro` | Conocer el reclamo y pasar de abierto a aprobado o rechazado |
| `Pago` | Conocer la fecha, el monto y el período pagado |

### 3.15 Separación de responsabilidades y programación estructurada

El programa está dividido en tres partes con responsabilidades separadas, lo que mantiene bajo el acoplamiento:

- **`objetos/`**: las clases del dominio, con las reglas del negocio. No saben nada de la base de datos ni de la consola.
- **`datos/`**: guarda los objetos en la base y los vuelve a construir a partir de ella.
- **`presentacion/`**: muestra los menús, pide los datos y les envía mensajes a los objetos.

La capa de presentación aplica también la **programación estructurada**: instrucciones que se ejecutan una tras otra, decisiones según condiciones y **bucles que se repiten hasta que se cumple una condición determinada**. Por ejemplo, cada función `pedir...` repite la pregunta hasta que el dato ingresado sea válido:

```python
def pedirSiNo(mensaje):
    while True:
        valor = input(mensaje + " (s/n): ").strip().lower()
        if valor in ("s", "n"):
            return valor == "s"
        print("Responda 's' o 'n'.")
```

---

## 4. Diagrama de clases

El diagrama de clases UML está en [`diagrama_clases.mmd`](diagrama_clases.mmd), en formato Mermaid. Muestra la vista estática del sistema:
- las siete clases, con sus atributos y operaciones
- la visibilidad (`-` privado, `+` público)
- los atributos y operaciones de clase (`$`) y el atributo derivado (`/edad`)
- la generalización de `Poliza`
- la asociación con `Cliente` y las composiciones con `Siniestro` y `Pago`, con su multiplicidad
- notas aclaratorias

Para verlo dibujado se puede abrir el archivo en [mermaid.live](https://mermaid.live) o en un editor con soporte para Mermaid.
