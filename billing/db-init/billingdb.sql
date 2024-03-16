--
-- Database: `billing`
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
 ("Navel", 93, "All"),
("Blood", 112, "All"),
("Mandarin", 104, "All"),
("Shamuti", 84, "All"),
("Tangerine", 92, "All"),
("Clementine", 113, "All"),
("Grapefruit", 88, "All"),
("Valencia", 87, "All"),
("Mandarin", 102, "43"),
("Mandarin", 120, "45"),
("Tangerine", 85, "12"),
("Valencia", 90, "45");

INSERT INTO `Trucks` (`id`, `provider_id`) VALUES 
('T-14409', 1),
('T-16474', 1),
('T-14964', 1),
('T-17194', 1),
('T-17250', 1),
('T-14045', 1),
('T-14263', 1),
('T-17164', 1),
('T-16810', 1),
('T-17077', 1),
('T-13972', 1),
('T-13982', 1),
('T-15689', 1),
('T-14664', 1),
('T-14623', 1),
('T-14873', 1),
('T-14064', 1),
('T-13799', 1),
('T-15861', 1),
('T-16584', 1),
('T-17267', 1),
('T-16617', 1),
('T-16270', 1),
('T-14969', 1),
('T-15521', 1),
('T-16556', 1),
('T-17744', 1),
('T-17412', 1),
('T-15733', 1),
('T-14091', 1),
('T-14129', 1);
