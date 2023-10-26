-- Tabla "Marcas"
CREATE TABLE Marcas (
    Id_Marca INT PRIMARY KEY AUTO_INCREMENT,
    Nombre_Marca VARCHAR(100),
    Descripcion_Marca TEXT
);

-- Tabla "Almacen"
CREATE TABLE Almacen (
    Id_Almacen INT PRIMARY KEY AUTO_INCREMENT,
    Nombre_Almacen VARCHAR(100),
    Ubicacion_Almacen VARCHAR(10)
);

-- Tabla "Contrato"
CREATE TABLE Contrato (
    Id_Contrato INT PRIMARY KEY AUTO_INCREMENT,
    Num_Contrato VARCHAR(100),
    Fecha_Inicio_Contrato DATE,
    Fecha_Fin_Contrato DATE
);

-- Tabla "Equipos"
CREATE TABLE Equipos (
    Id_Equipo INT PRIMARY KEY AUTO_INCREMENT,
    Id_Marca INT,
    Id_Almacen INT,
    Id_Contrato INT,
    Fecha_Registro DATE,
    Tipo_Equipo VARCHAR(100),
    Modelo VARCHAR(100),
    Caracteristicas TEXT,
    Num_Serie VARCHAR(100),
    Num_Parte VARCHAR(100),
    Funciona INT,
    Estado VARCHAR(50),
    FOREIGN KEY (Id_Marca) REFERENCES Marcas(Id_Marca),
    FOREIGN KEY (Id_Almacen) REFERENCES Almacen(Id_Almacen),
    FOREIGN KEY (Id_Contrato) REFERENCES Contrato(Id_Contrato)
);

-- Tabla "Piezas_Componentes"
CREATE TABLE Piezas_Componentes (
    Id_Componente INT PRIMARY KEY AUTO_INCREMENT,
    Id_Equipo INT,
    Id_Marca INT,
    Id_Almacen INT,
    Id_Contrato INT,
    Fecha_Registro DATE,
    Tipo_Pieza VARCHAR(100),
    Cantidad INT,
    Modelo VARCHAR(100),
    Caracteristicas TEXT,
    Num_Serie VARCHAR(100),
    Num_Parte VARCHAR(100),
    Funciona INT,
    Estado VARCHAR(50),
    FOREIGN KEY (Id_Equipo) REFERENCES Equipos(Id_Equipo),
    FOREIGN KEY (Id_Marca) REFERENCES Marcas(Id_Marca),
    FOREIGN KEY (Id_Almacen) REFERENCES Almacen(Id_Almacen),
    FOREIGN KEY (Id_Contrato) REFERENCES Contrato(Id_Contrato)
);

-- Tabla "Inventario"
CREATE TABLE Inventario (
    Id_Inventario INT PRIMARY KEY AUTO_INCREMENT,
    Id_Equipo INT,
    Id_Componente INT,
    Id_Almacen INT,
    Fecha_Registro DATE,
    FOREIGN KEY (Id_Equipo) REFERENCES Equipos(Id_Equipo),
    FOREIGN KEY (Id_Componente) REFERENCES Piezas_Componentes(Id_Componente),
    FOREIGN KEY (Id_Almacen) REFERENCES Almacen(Id_Almacen)
);
