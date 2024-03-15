--
-- Database: `billdb`
--

CREATE DATABASE IF NOT EXISTS `billing`;
USE `billing`;

-- --------------------------------------------------------

--
-- Table structure
--

CREATE TABLE IF NOT EXISTS `Provider` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  AUTO_INCREMENT=10001 ;

CREATE TABLE IF NOT EXISTS `Rates` (
  `product_id` varchar(50) NOT NULL,
  `rate` int(11) DEFAULT 0,
  `scope` varchar(50) DEFAULT NULL,
  FOREIGN KEY (scope) REFERENCES `Provider`(`id`)
) ENGINE=MyISAM ;

CREATE TABLE IF NOT EXISTS `Trucks` (
  `id` varchar(10) NOT NULL,
  `provider_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`provider_id`) REFERENCES `Provider`(`id`)
) ENGINE=MyISAM ;
--
-- Dumping data
--

INSERT INTO `Provider` (`name`) VALUES 
('Provider 1'),
('Provider 2'),
('Provider 3');

INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES 
('Product1', 100, '1'),
('Product2', 150, '2'),
('Product3', 200, 'ALL');

INSERT INTO `Trucks` (`id`, `provider_id`) VALUES 
('TRUCK001', 1),
('TRUCK002', 2),
('TRUCK003', NULL);
