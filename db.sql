-- Base de datos: db_sistema_impuestos

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- --------------------------------------------------------
-- Tabla `clientes`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientes` (
  `idCliente` int(10) NOT NULL AUTO_INCREMENT,
  `codigo` char(10) NOT NULL,
  `nombre` char(100) NOT NULL,
  `direccion` char(150) NOT NULL,
  `telefono` char(10) NOT NULL,
  `email` char(150) NOT NULL,
  `tipo` char(10) NOT NULL DEFAULT 'particular',
  PRIMARY KEY (`idCliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Clientes iniciales
INSERT INTO `clientes` (`idCliente`, `codigo`, `nombre`, `direccion`, `telefono`, `email`, `tipo`) VALUES
(1, '001', 'Luis Hernandez', 'Usulutan', '4545-3256', 'luishernandez@ugb.edu.sv', 'particular')
ON DUPLICATE KEY UPDATE `nombre`=VALUES(`nombre`);

INSERT INTO `clientes` (`idCliente`, `codigo`, `nombre`, `direccion`, `telefono`, `email`, `tipo`) VALUES
(2, 'EMP-001', 'Comercializadora El Progreso S.A. de C.V.', 'San Salvador', '2255-7788', 'contacto@elprogreso.com', 'empresa'),
(3, 'EMP-002', 'Industrias Salvadoreñas S.A. de C.V.', 'San Miguel', '2660-1234', 'info@industrias-sv.com', 'empresa')
ON DUPLICATE KEY UPDATE `nombre`=VALUES(`nombre`);

-- --------------------------------------------------------
-- Tabla `productos`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `productos` (
  `codigo` char(10) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `productos` (`codigo`, `nombre`, `tipo`) VALUES
('11801', 'Impuesto a las Actividades Económicas - Comercio', 'comercio'),
('11802', 'Impuesto a las Actividades Económicas - Industria', 'industria')
ON DUPLICATE KEY UPDATE `nombre`=VALUES(`nombre`);

-- --------------------------------------------------------
-- Tabla `tarifas`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `tarifas` (
  `idTarifa` int(11) NOT NULL AUTO_INCREMENT,
  `codigoProducto` char(10) NOT NULL,
  `desde` decimal(14,2) NOT NULL,
  `hasta` decimal(14,2) NOT NULL,
  `precioBase` decimal(10,2) NOT NULL,
  `adicional` decimal(10,2) NOT NULL,
  `porcentaje` decimal(5,2) NOT NULL DEFAULT 0.00,
  `vigente` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`idTarifa`),
  KEY `idx_producto_rango` (`codigoProducto`, `desde`, `hasta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Limpiar tarifas para evitar duplicados en reinicios de script
DELETE FROM `tarifas`;

-- Tarifas oficiales segun Seccion 8 del Documento de Requerimiento (para 11801 Comercio y 11802 Industria)
-- NOTA: El rango de 6,000.01 a 8,000.00 queda intencionalmente sin configurar segun Seccion 18.2 y CA 10.
INSERT INTO `tarifas` (`codigoProducto`, `desde`, `hasta`, `precioBase`, `adicional`, `porcentaje`, `vigente`) VALUES
('11801', 0.01, 500.00, 1.50, 0.00, 0.00, 1),
('11801', 500.01, 1000.00, 1.50, 3.00, 0.00, 1),
('11801', 1000.01, 2000.00, 3.00, 3.00, 0.00, 1),
('11801', 2000.01, 3000.00, 6.00, 3.00, 0.00, 1),
('11801', 3000.01, 6000.00, 9.00, 2.00, 0.00, 1),
('11801', 8000.01, 18000.00, 15.00, 2.00, 0.00, 1),
('11801', 18000.01, 30000.00, 39.00, 2.00, 0.00, 1),
('11801', 30000.01, 60000.00, 63.00, 1.00, 0.00, 1),
('11801', 60000.01, 100000.00, 93.00, 0.80, 0.00, 1),
('11801', 100000.01, 200000.00, 125.00, 0.70, 0.00, 1),
('11801', 200000.01, 300000.00, 195.00, 0.60, 0.00, 1),
('11801', 300000.01, 400000.00, 255.00, 0.45, 0.00, 1),
('11801', 400000.01, 500000.00, 300.00, 0.40, 0.00, 1),
('11801', 500000.01, 1000000.00, 340.00, 0.30, 0.00, 1),
('11801', 1000000.01, 99999999.99, 490.00, 0.18, 0.00, 1),

-- Tarifas para 11802 Industria (mismo esquema base)
('11802', 0.01, 500.00, 1.50, 0.00, 0.00, 1),
('11802', 500.01, 1000.00, 1.50, 3.00, 0.00, 1),
('11802', 1000.01, 2000.00, 3.00, 3.00, 0.00, 1),
('11802', 2000.01, 3000.00, 6.00, 3.00, 0.00, 1),
('11802', 3000.01, 6000.00, 9.00, 2.00, 0.00, 1),
('11802', 8000.01, 18000.00, 15.00, 2.00, 0.00, 1),
('11802', 18000.01, 30000.00, 39.00, 2.00, 0.00, 1),
('11802', 30000.01, 60000.00, 63.00, 1.00, 0.00, 1),
('11802', 60000.01, 100000.00, 93.00, 0.80, 0.00, 1),
('11802', 100000.01, 200000.00, 125.00, 0.70, 0.00, 1),
('11802', 200000.01, 300000.00, 195.00, 0.60, 0.00, 1),
('11802', 300000.01, 400000.00, 255.00, 0.45, 0.00, 1),
('11802', 400000.01, 500000.00, 300.00, 0.40, 0.00, 1),
('11802', 500000.01, 1000000.00, 340.00, 0.30, 0.00, 1),
('11802', 1000000.01, 99999999.99, 490.00, 0.18, 0.00, 1);

-- --------------------------------------------------------
-- Tabla `periodos_actividades_economicas`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `periodos_actividades_economicas` (
  `idPeriodo` int(11) NOT NULL AUTO_INCREMENT,
  `idCliente` int(10) NOT NULL,
  `codigoProducto` char(10) NOT NULL,
  `desde` date NOT NULL,
  `hasta` date NOT NULL,
  `balance` decimal(14,2) NOT NULL,
  `cantidad` decimal(10,2) NOT NULL DEFAULT 1.00,
  `precio` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `estado` varchar(30) NOT NULL DEFAULT 'Vigente',
  `tarifaRango` varchar(100) DEFAULT NULL,
  `formulaAplicada` varchar(255) DEFAULT NULL,
  `esFacturado` tinyint(1) NOT NULL DEFAULT 0,
  `usuario` varchar(50) NOT NULL DEFAULT 'admin',
  `fechaCreacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `notas` text DEFAULT NULL,
  PRIMARY KEY (`idPeriodo`),
  KEY `idx_cliente_producto` (`idCliente`, `codigoProducto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Limpiar periodos para datos de prueba iniciales
DELETE FROM `periodos_actividades_economicas`;

-- Registro historico oficial de la Seccion 7 del Documento para el cliente 2 (EMP-001)
-- Suma de precios = $2.10 + $4.50 + $4.50 + $4.50 + $4.50 = $20.10 (Total referencial)
INSERT INTO `periodos_actividades_economicas` (`idCliente`, `codigoProducto`, `desde`, `hasta`, `balance`, `cantidad`, `precio`, `subtotal`, `estado`, `tarifaRango`, `formulaAplicada`, `esFacturado`, `usuario`) VALUES
(2, '11801', '2022-01-01', '2023-01-01', 700.00, 1.00, 2.10, 2.10, 'Histórico', '$500.01 a $1,000.00', '1.50 + ((700.00 - 500.00) / 1,000 x 3.00) = $2.10 [Histórica]', 1, 'admin'),
(2, '11801', '2023-01-01', '2024-01-01', 545.00, 1.00, 4.50, 4.50, 'Histórico', '$500.01 a $1,000.00', '1.50 + (1 x 3.00) = $4.50 [CEIL]', 1, 'admin'),
(2, '11801', '2024-01-01', '2025-01-01', 550.00, 1.00, 4.50, 4.50, 'Histórico', '$500.01 a $1,000.00', '1.50 + (1 x 3.00) = $4.50 [CEIL]', 1, 'admin'),
(2, '11801', '2025-01-01', '2026-01-01', 550.00, 1.00, 4.50, 4.50, 'Histórico', '$500.01 a $1,000.00', '1.50 + (1 x 3.00) = $4.50 [CEIL]', 1, 'admin'),
(2, '11801', '2026-01-01', '2027-01-01', 550.00, 1.00, 4.50, 4.50, 'Vigente', '$500.01 a $1,000.00', '1.50 + (1 x 3.00) = $4.50 [CEIL]', 0, 'admin');

-- --------------------------------------------------------
-- Tabla `auditoria_periodos`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `auditoria_periodos` (
  `idAuditoria` int(11) NOT NULL AUTO_INCREMENT,
  `idPeriodo` int(11) NOT NULL,
  `accion` varchar(50) NOT NULL,
  `balanceAnterior` decimal(14,2) DEFAULT NULL,
  `balanceNuevo` decimal(14,2) DEFAULT NULL,
  `precioAnterior` decimal(10,2) DEFAULT NULL,
  `precioNuevo` decimal(10,2) DEFAULT NULL,
  `motivo` varchar(255) DEFAULT NULL,
  `usuario` varchar(50) NOT NULL DEFAULT 'admin',
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idAuditoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

COMMIT;
