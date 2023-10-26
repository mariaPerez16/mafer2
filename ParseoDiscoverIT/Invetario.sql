CREATE DATABASE IF NOT EXISTS `Invetario_IT` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE Invetario_IT;
CREATE TABLE Marca(
    idMarca INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    PRIMARY KEY (idMarca)
);
CREATE TABLE Tipo(
    idTipo INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    PRIMARY KEY (idTipo)
);
CREATE TABLE Modelo(
    idModelo INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    PRIMARY KEY (idModelo)
);
CREATE TABLE Estado(
    idEstado INT NOT NULL AUTO_INCREMENT,
    Estado VARCHAR(20) NOT NULL,
    Funcional BOOLEAN NOT NULL,
    PRIMARY KEY (idEstado)
);
CREATE TABLE Lugar(
    idLugar INT NOT NULL AUTO_INCREMENT,
    lugar VARCHAR(45) NOT NULL,
    PRIMARY KEY (idLugar)
);
CREATE TABLE Almacen(
    idAlmacen INT NOT NULL AUTO_INCREMENT,
    fecha_registro DATE NOT NULL,
    fecha_consulta DATE,
    idLugar INT NOT NULL,
    PRIMARY KEY (idAlmacen),
    FOREIGN KEY (idLugar) REFERENCES Lugar(idLugar)
);
CREATE TABLE Equipos(
    idEquipo INT NOT NULL AUTO_INCREMENT,
    numero_serie VARCHAR(15) NOT NULL,
    numero_parte VARCHAR(15) NOT NULL,
    caracteristicas VARCHAR(50),
    version_software VARCHAR(15) NOT NULL,
    comentarios VARCHAR(50),
    idMarca INT NOT NULL,
    idModelo INT NOT NULL,
    idTipo INT NOT NULL,
    idEstado INT NOT NULL,
    idAlmacen INT NOT NULL,
    PRIMARY KEY (idEquipo),
    FOREIGN KEY (idMarca) REFERENCES Marca(idMarca),
    FOREIGN KEY (idModelo) REFERENCES Modelo(idModelo),
    FOREIGN KEY (idTipo) REFERENCES Tipo(idTipo),
    FOREIGN KEY (idEstado) REFERENCES Estado(idEstado),
    FOREIGN KEY (idAlmacen) REFERENCES Almacen(idAlmacen)
);

CREATE TABLE Devoluciones(
    idDevolucion INT NOT NULL AUTO_INCREMENT,
    fecha_devolucion DATE,
    idEquipo INT NOT NULL,
    idEstado INT,
    PRIMARY KEY (idDevolucion),
    FOREIGN KEY (idEstado) REFERENCES Estado(idEstado),
    FOREIGN KEY (idEquipo) REFERENCES Equipos(idEquipo)
);

CREATE TABLE Contratos(
    idContrato INT NOT NULL AUTO_INCREMENT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    idEquipo INT NOT NULL,
    comentarios VARCHAR(45),
    PRIMARY KEY (idContrato),
    FOREIGN KEY (idEquipo) REFERENCES Equipos(idEquipo)
);

CREATE TABLE Piezas(
    idPieza INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    numero_parte VARCHAR(15) NOT NULL,
    numero_serie VARCHAR(15) NOT NULL,
    idEquipo INT NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (idPieza),
    FOREIGN KEY (idEquipo) REFERENCES Equipos(idEquipo)
);
SHOW TABLES;