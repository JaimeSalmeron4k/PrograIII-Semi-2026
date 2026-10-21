-- ========================================================
-- Base de Datos: db_academica
-- ========================================================

CREATE DATABASE IF NOT EXISTS `db_academica` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `db_academica`;

-- --------------------------------------------------------
-- Estructura de tabla para `usuarios_usss014225`
-- Requerimiento 1:
--   a. idUsuario int(10) A_I
--   b. usuario char(35)
--   c. clave char(35)
--   d. nombre char(85)
--   e. dirección char(100)
--   f. teléfono char(9)
-- --------------------------------------------------------

DROP TABLE IF EXISTS `usuarios_usss014225`;

CREATE TABLE `usuarios_usss014225` (
  `idUsuario` INT(10) NOT NULL AUTO_INCREMENT,
  `usuario` CHAR(35) NOT NULL,
  `clave` CHAR(35) NOT NULL,
  `nombre` CHAR(85) NOT NULL,
  `direccion` CHAR(100) NOT NULL,
  `telefono` CHAR(9) NOT NULL,
  `dirección` CHAR(100) NOT NULL DEFAULT '',
  `teléfono` CHAR(9) NOT NULL DEFAULT '',
  PRIMARY KEY (`idUsuario`),
  UNIQUE KEY `uk_usuario` (`usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Triggers para garantizar compatibilidad total con o sin tildes en columnas
DELIMITER $$
CREATE TRIGGER `trg_usuarios_usss014225_bi` BEFORE INSERT ON `usuarios_usss014225`
FOR EACH ROW
BEGIN
    IF NEW.direccion = '' AND NEW.`dirección` <> '' THEN
        SET NEW.direccion = NEW.`dirección`;
    ELSEIF NEW.`dirección` = '' AND NEW.direccion <> '' THEN
        SET NEW.`dirección` = NEW.direccion;
    END IF;

    IF NEW.telefono = '' AND NEW.`teléfono` <> '' THEN
        SET NEW.telefono = NEW.`teléfono`;
    ELSEIF NEW.`teléfono` = '' AND NEW.telefono <> '' THEN
        SET NEW.`teléfono` = NEW.telefono;
    END IF;
END$$

CREATE TRIGGER `trg_usuarios_usss014225_bu` BEFORE UPDATE ON `usuarios_usss014225`
FOR EACH ROW
BEGIN
    IF NEW.direccion <> OLD.direccion THEN
        SET NEW.`dirección` = NEW.direccion;
    ELSEIF NEW.`dirección` <> OLD.`dirección` THEN
        SET NEW.direccion = NEW.`dirección`;
    END IF;

    IF NEW.telefono <> OLD.telefono THEN
        SET NEW.`teléfono` = NEW.telefono;
    ELSEIF NEW.`teléfono` <> OLD.`teléfono` THEN
        SET NEW.telefono = NEW.`teléfono`;
    END IF;
END$$
DELIMITER ;

-- --------------------------------------------------------
-- Datos de prueba iniciales para la tabla `usuarios_usss014225`
-- --------------------------------------------------------

INSERT INTO `usuarios_usss014225` (`usuario`, `clave`, `nombre`, `direccion`, `telefono`, `dirección`, `teléfono`) VALUES
('admin', 'admin123', 'Administrador del Sistema', 'Campus UGB Usulután', '7123-4567', 'Campus UGB Usulután', '7123-4567'),
('USSS014225', 'SalmeronUGB2025@', 'Jaime Salmeron', 'Usulután, El Salvador', '7890-1234', 'Usulután, El Salvador', '7274-4374');
