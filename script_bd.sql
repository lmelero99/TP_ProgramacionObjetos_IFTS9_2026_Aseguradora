-- Ejecutar una sola vez para crear la base de datos y las tablas
CREATE DATABASE IF NOT EXISTS aseguradora;
USE aseguradora;

CREATE TABLE IF NOT EXISTS clientes (
    dni              VARCHAR(10)  PRIMARY KEY,
    nombre           VARCHAR(50)  NOT NULL,
    apellido         VARCHAR(50)  NOT NULL,
    fecha_nacimiento DATE         NOT NULL,
    telefono         VARCHAR(20),
    email            VARCHAR(80)
);

-- Catálogo de tipos de póliza (datos fijos, precargados abajo)
CREATE TABLE IF NOT EXISTS poliza_tipo (
    id               INT          PRIMARY KEY,
    nombre           VARCHAR(10)  NOT NULL UNIQUE,   -- coincide con el atributo TIPO de cada clase
    descripcion      VARCHAR(50)  NOT NULL
);

INSERT IGNORE INTO poliza_tipo (id, nombre, descripcion) VALUES
    (1, 'auto',  'Seguro automotor'),
    (2, 'hogar', 'Seguro de hogar'),
    (3, 'vida',  'Seguro de vida');

-- Catálogo de estados guardados de una póliza. "vencida" no se guarda: se calcula con fecha_fin.
CREATE TABLE IF NOT EXISTS poliza_estado (
    id               INT          PRIMARY KEY,
    nombre           VARCHAR(10)  NOT NULL UNIQUE    -- coincide con las constantes de la clase Poliza
);

INSERT IGNORE INTO poliza_estado (id, nombre) VALUES
    (1, 'vigente'),
    (2, 'cancelada');

-- Datos comunes a todas las pólizas (clase Poliza)
CREATE TABLE IF NOT EXISTS polizas (
    numero           INT AUTO_INCREMENT PRIMARY KEY,
    id_tipo          INT          NOT NULL,
    dni_cliente      VARCHAR(10)  NOT NULL,
    fecha_inicio     DATE         NOT NULL,
    fecha_fin        DATE         NOT NULL,
    suma_asegurada   DECIMAL(14,2) NOT NULL,
    id_estado        INT          NOT NULL,
    CONSTRAINT fk_poliza_tipo    FOREIGN KEY (id_tipo)     REFERENCES poliza_tipo(id),
    CONSTRAINT fk_poliza_estado  FOREIGN KEY (id_estado)   REFERENCES poliza_estado(id),
    CONSTRAINT fk_poliza_cliente FOREIGN KEY (dni_cliente) REFERENCES clientes(dni)
);

-- Datos propios de cada clase hija; "numero" es a la vez PK y FK a polizas
CREATE TABLE IF NOT EXISTS polizas_auto (
    numero           INT          PRIMARY KEY,
    patente          VARCHAR(10)  NOT NULL,
    marca            VARCHAR(30)  NOT NULL,
    modelo           VARCHAR(30)  NOT NULL,
    anio             INT          NOT NULL,
    CONSTRAINT fk_auto_poliza FOREIGN KEY (numero) REFERENCES polizas(numero)
);

CREATE TABLE IF NOT EXISTS polizas_hogar (
    numero           INT          PRIMARY KEY,
    direccion        VARCHAR(100) NOT NULL,
    metros_cuadrados INT          NOT NULL,
    CONSTRAINT fk_hogar_poliza FOREIGN KEY (numero) REFERENCES polizas(numero)
);

CREATE TABLE IF NOT EXISTS polizas_vida (
    numero           INT          PRIMARY KEY,
    beneficiario     VARCHAR(80)  NOT NULL,
    edad_asegurado   INT          NOT NULL,
    CONSTRAINT fk_vida_poliza FOREIGN KEY (numero) REFERENCES polizas(numero)
);

-- Catálogo de estados de un siniestro
CREATE TABLE IF NOT EXISTS siniestro_estado (
    id               INT          PRIMARY KEY,
    nombre           VARCHAR(10)  NOT NULL UNIQUE    -- coincide con las constantes de la clase Siniestro
);

INSERT IGNORE INTO siniestro_estado (id, nombre) VALUES
    (1, 'abierto'),
    (2, 'aprobado'),
    (3, 'rechazado');

CREATE TABLE IF NOT EXISTS siniestros (
    numero          INT AUTO_INCREMENT PRIMARY KEY,
    numero_poliza   INT          NOT NULL,
    fecha           DATE         NOT NULL,
    descripcion     VARCHAR(200) NOT NULL,
    monto_reclamado DECIMAL(14,2) NOT NULL,
    id_estado       INT          NOT NULL,
    CONSTRAINT fk_siniestro_poliza FOREIGN KEY (numero_poliza) REFERENCES polizas(numero),
    CONSTRAINT fk_siniestro_estado FOREIGN KEY (id_estado)     REFERENCES siniestro_estado(id)
);

CREATE TABLE IF NOT EXISTS pagos (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    numero_poliza INT          NOT NULL,
    fecha         DATE         NOT NULL,
    monto         DECIMAL(14,2) NOT NULL,
    periodo       VARCHAR(7)   NOT NULL,             -- formato AAAA-MM
    CONSTRAINT fk_pago_poliza FOREIGN KEY (numero_poliza) REFERENCES polizas(numero)
);
