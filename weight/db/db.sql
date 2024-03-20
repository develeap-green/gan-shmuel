--
-- Database: `Weight`
--

CREATE DATABASE IF NOT EXISTS `weight`;

-- --------------------------------------------------------

--
-- Table structure for table `containers-registered`
--

USE weight;

CREATE TABLE IF NOT EXISTS `containers_registered` (
  `container_id` varchar(15) NOT NULL,
  `weight` int(12) DEFAULT NULL,
  `unit` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`container_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10001 ;

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE IF NOT EXISTS `transactions` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `datetime` datetime DEFAULT NULL,
  `direction` varchar(10) DEFAULT NULL,
  `truck` varchar(50) DEFAULT NULL,
  `containers` varchar(10000) DEFAULT NULL,
  `bruto` int(12) DEFAULT NULL,
  `truckTara` int(12) DEFAULT NULL,
  --   "neto": <int> or NULL // na if some of containers unknown
  `neto` int(12) DEFAULT NULL,
  `produce` varchar(50) DEFAULT NULL,
  `session_id` int(12) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10001 ;

INSERT INTO containers_registered (container_id, weight, unit)
VALUES
    ('C-001', 100, 'kg'),
    ('C-002', 100, 'kg'),
    ('C-003', 100, 'kg'),
    ('C-004', 100, 'kg'),
    ('C-005', 100, 'kg'),
    ('C-006', 100, 'kg'),
    ('C-007', 100, 'kg'),
    ('C-008', 100, 'kg'),
    ('C-009', 100, 'kg'),
    ('C-010', 100, 'kg'),
    ('C-011', 100, 'kg'),
    ('C-012', 100, 'kg'),
    ('C-013', 100, 'kg'),
    ('C-014', 100, 'kg'),
    ('C-015', 100, 'kg'),
    ('C-016', 100, 'kg'),
    ('C-017', 100, 'kg'),
    ('C-018', 100, 'kg'),
    ('C-019', 100, 'kg'),
    ('C-020', 100, 'kg');
   


INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce, session_id)
VALUES 
    ('2024-03-20 08:10:17', 'in', 'T-0001', 'C-001,C-002,C-003', 5000, NULL, NULL, 'orange', 401300),
    ('2024-03-20 08:10:51', 'out', 'T-0001', 'C-001,C-002,C-003', 5000, 500, 4200, 'orange', 401300),
    ('2024-03-20 08:12:04', 'none', NULL, 'C-004', 5000, NULL, 4900, 'orange', 4104971),
    ('2024-03-20 08:28:04', 'in', 'T-0002', 'C-005,C-006,C-007', 2500, NULL, NULL, 'Apple', 9407909),
    ('2024-03-20 08:28:11', 'out', 'T-0002', 'C-005,C-006,C-007', 2500, 600, 1600, 'Apple', 9407909),
    ('2024-03-20 08:29:32', 'in', 'T-0003', 'C-008,C-009,C-010', 3100, NULL, NULL, 'Tomatoes', 7169365),
    ('2024-03-20 08:29:49', 'out', 'T-0003', 'C-008,C-009,C-010', 3100, 1000, 1800, 'Tomatoes', 7169365),
    ('2024-03-20 08:31:23', 'none', NULL, 'C-011', 500, NULL, 400, 'Onion', 1372756),
    ('2024-03-20 08:32:15', 'in', 'T-0004', 'C-012,C-013,C-014', 4256, NULL, NULL, 'Potato', 7908684),
    ('2024-03-20 08:32:41', 'out', 'T-0004', 'C-012,C-013,C-014', 4256, 1000, 2956, 'Potato', 7908684),
    ('2024-03-20 08:33:29', 'none', NULL, 'C-015', 700, NULL, 600, 'Onion', 4093691),
    ('2024-03-20 08:34:05', 'in', 'T-0005', 'C-016,C-017,C-018', 3248, NULL, NULL, 'Lettuce', 2096663),
    ('2024-03-20 08:34:24', 'out', 'T-0005', 'C-016,C-017,C-018', 3248, 1423, 1525, 'Lettuce', 2096663),
    ('2024-03-20 08:35:02', 'none', NULL, 'C-019', 254, NULL, 154, 'Celery', 3200468),
    ('2024-03-20 09:39:39', 'in', 'T-2222', 'C-002', 800, NULL, NULL, 'Lettuce', 9857905),
    ('2024-03-20 09:44:29', 'out', 'T-2222', 'C-002', 800, 200, 500, 'Lettuce', 9857905),
    ('2024-03-20 09:45:12', 'in', 'T-3333', 'C-003', 1000, NULL, NULL, 'Lettuce', 6389386),
    ('2024-03-20 09:45:47', 'out', 'T-3333', 'C-003', 1000, 100, 800, 'Lettuce', 6389386),
    ('2024-03-20 09:46:03', 'in', 'T-4444', 'C-004', 1000, NULL, NULL, 'Lettuce', 2817415),
    ('2024-03-20 09:46:21', 'out', 'T-4444', 'C-004', 1000, 300, 600, 'Lettuce', 2817415),
    ('2024-03-20 09:46:36', 'in', 'T-5555', 'C-005', 600, NULL, NULL, 'Lettuce', 1197226),
    ('2024-03-20 09:46:53', 'out', 'T-5555', 'C-005', 600, 300, 200, 'Lettuce', 1197226),
    ('2024-03-20 09:47:09', 'in', 'T-6666', 'C-006', 900, NULL, NULL, 'Lettuce', 4387196),
    ('2024-03-20 09:47:28', 'out', 'T-6666', 'C-006', 900, 200, 600, 'Lettuce', 4387196);