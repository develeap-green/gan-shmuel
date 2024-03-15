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

show tables;

describe containers_registered;
describe transactions;



--
-- Dumping data for table `test`
--

INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0918591', 1482, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0903812', 641, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0952882', 1351, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0867487', 563, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0280066', 1380, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0722514', 1376, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0690183', 1180, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0290725', 1474, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0625825', 1319, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0894574', 1244, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0894682', 752, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0360359', 1393, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0508382', 935, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0894160', 567, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0451407', 817, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0577318', 847, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0936917', 1205, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0211080', 813, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0898519', 578, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0480555', 983, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0723848', 1040, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0813811', 866, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0923132', 652, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0615348', 788, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0536607', 1185, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0535215', 689, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0402642', 1043, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0794677', 606, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0781208', 1396, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0529566', 1055, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0653112', 563, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0949899', 1291, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0784016', 897, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0258544', 1381, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0169739', 783, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0647344', 1021, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0259857', 1032, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0212527', 615, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0555979', 1371, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0103679', 549, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0550343', 699, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0907080', 756, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0997392', 1353, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0576278', 912, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0287536', 704, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0722860', 1337, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0447944', 1047, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0477829', 1240, 'kg');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0111995', 1401, 'lbs');
INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES ('C-0745069', 1196, 'lbs');

-- Transactions Inserts
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-11 12:38:38', 'out', 'T-18186', 'C-0794677,C-0781208,C-0690183', 5647, 1765, 700, 'Mangoes', 7781);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-15 17:07:42', 'in', 'T-15083', 'C-0447944,C-0211080', 4088, 1381, 847, 'Apples', 8119);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-10 23:13:05', 'out', 'T-54612', 'C-0923132,C-0280066', 4655, 1831, 792, 'Oranges', 8621);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-08 10:24:55', 'in', 'T-17464', 'C-0480555,C-0907080,C-0952882', 5982, 1385, 1507, 'Bananas', 4943);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 12:13:49', 'out', 'T-23676', 'C-0745069', 3595, 1390, 1009, 'Oranges', 4991);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-15 20:27:10', 'in', 'T-53510', 'C-0690183,C-0480555', 4312, 1596, 553, 'Grapes', 8493);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-07 12:48:02', 'out', 'T-43277', 'C-0949899,C-0480555,C-0259857,C-0625825', 8956, 2377, 1954, 'Mangoes', 8394);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-10 06:50:19', 'out', 'T-89625', 'C-0723848,C-0936917,C-0259857', 6404, 2438, 689, 'Apples', 5425);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-05 19:59:58', 'in', 'T-56802', 'C-0936917,C-0211080,C-0447944,C-0625825', 8574, 2546, 1644, 'Grapes', 8343);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-11 23:08:28', 'none', 'T-79950', 'C-0949899,C-0745069,C-0550343,C-0923132', 8519, 2742, 1939, 'Oranges', 3468);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 14:35:43', 'in', 'T-69637', 'C-0211080,C-0550343,C-0894574,C-0949899', 7340, 2394, 899, 'Apples', 8591);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-06 13:59:16', 'none', 'T-74267', 'C-0480555,C-0111995,C-0723848', 5104, 1070, 610, 'Oranges', 1853);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-06 12:42:33', 'out', 'T-17892', 'C-0477829,C-0212527,C-0794677', 6125, 2824, 840, 'Bananas', 9839);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-13 11:26:16', 'in', 'T-42739', 'C-0447944,C-0508382', 5214, 1776, 1456, 'Oranges', 7449);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-05 10:47:07', 'none', 'T-54068', 'C-0997392', 3872, 1084, 1435, 'Grapes', 5790);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-11 01:49:58', 'none', 'T-67846', 'C-0898519,C-0536607,C-0360359,C-0508382', 7779, 2669, 1019, 'Oranges', 1801);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-01 00:43:48', 'in', 'T-25401', 'C-0576278', 4799, 2314, 1573, 'Grapes', 1099);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-12 20:21:36', 'in', 'T-72594', 'C-0169739', 3595, 1869, 943, 'Apples', 6414);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-08 03:33:21', 'none', 'T-98705', 'C-0287536,C-0480555', 4927, 1793, 1447, 'Apples', 4102);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-08 17:11:48', 'out', 'T-36094', 'C-0280066,C-0576278,C-0918591,C-0212527', 8183, 2298, 1496, 'Mangoes', 2122);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-07 22:11:32', 'out', 'T-62975', 'C-0784016,C-0867487,C-0647344,C-0451407', 7243, 1950, 1995, 'Apples', 3961);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-07 16:02:17', 'out', 'T-41107', 'C-0898519,C-0745069', 4575, 1524, 1277, 'Oranges', 5169);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-02 13:25:43', 'out', 'T-46962', 'C-0529566,C-0360359,C-0722860', 7452, 2628, 1039, 'Apples', 7089);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-07 19:21:07', 'in', 'T-43655', 'C-0615348', 3383, 1553, 1042, 'Grapes', 5251);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-02 19:34:10', 'none', 'T-55694', 'C-0550343', 4742, 2345, 1698, 'Apples', 4667);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-04 11:57:17', 'out', 'T-61115', 'C-0894682,C-0936917,C-0447944,C-0555979', 6942, 2011, 556, 'Bananas', 2795);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-15 17:26:31', 'out', 'T-66235', 'C-0550343,C-0212527,C-0894574', 6230, 2900, 772, 'Bananas', 3548);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 16:56:58', 'none', 'T-31968', 'C-0555979,C-0550343', 6169, 2234, 1865, 'Grapes', 1918);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-01 10:46:05', 'none', 'T-89883', 'C-0923132,C-0576278', 5380, 1850, 1966, 'Bananas', 6866);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-04 11:52:18', 'out', 'T-22830', 'C-0903812,C-0907080,C-0894682,C-0508382', 5852, 1819, 949, 'Grapes', 2080);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-06 23:55:26', 'in', 'T-56747', 'C-0647344,C-0898519,C-0477829', 5545, 1235, 1471, 'Oranges', 7858);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-03 08:15:59', 'out', 'T-56273', 'C-0923132,C-0451407,C-0576278,C-0794677', 6314, 1467, 1860, 'Grapes', 3247);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-06 00:04:46', 'out', 'T-29653', 'C-0894574,C-0103679,C-0949899,C-0290725', 9117, 2644, 1915, 'Bananas', 9641);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-10 10:15:46', 'in', 'T-92768', 'C-0898519,C-0615348', 3984, 1038, 1580, 'Mangoes', 8096);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-04 07:29:48', 'in', 'T-13574', 'C-0813811,C-0894682', 3487, 1364, 505, 'Grapes', 5633);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-05 10:38:13', 'none', 'T-88123', 'C-0550343,C-0723848,C-0280066,C-0923132', 5686, 1403, 512, 'Grapes', 8464);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-02 05:46:40', 'none', 'T-84405', 'C-0259857,C-0936917', 5672, 2831, 604, 'Oranges', 1586);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-12 06:37:00', 'in', 'T-44841', 'C-0653112,C-0360359,C-0918591,C-0211080,C-0212527', 8993, 2813, 1314, 'Mangoes', 1377);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-07 21:59:50', 'in', 'T-72192', 'C-0867487,C-0550343,C-0402642,C-0781208', 7030, 2802, 527, 'Bananas', 7559);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-10 19:50:23', 'out', 'T-20002', 'C-0907080,C-0169739,C-0952882,C-0555979,C-0576278', 8799, 2719, 907, 'Oranges', 2655);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-08 05:40:56', 'none', 'T-79895', 'C-0103679,C-0690183,C-0653112,C-0625825,C-0550343', 6945, 1410, 1225, 'Mangoes', 3061);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-07 09:03:53', 'none', 'T-87509', 'C-0936917', 3545, 1621, 719, 'Bananas', 6726);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-01 09:15:16', 'out', 'T-87247', 'C-0918591,C-0894574,C-0211080', 7906, 2398, 1969, 'Mangoes', 7868);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-05 13:30:23', 'none', 'T-39571', 'C-0103679,C-0259857,C-0936917', 5442, 1248, 1408, 'Apples', 1097);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 07:51:52', 'none', 'T-15815', 'C-0918591,C-0447944,C-0722860,C-0653112,C-0287536', 7691, 1959, 599, 'Bananas', 5013);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 04:13:29', 'out', 'T-20183', 'C-0577318,C-0647344', 5480, 2471, 1141, 'Apples', 6998);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-11 03:28:32', 'none', 'T-41153', 'C-0508382', 2669, 1089, 645, 'Oranges', 1658);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-05 14:00:38', 'out', 'T-63300', 'C-0211080,C-0936917,C-0169739', 6748, 1971, 1976, 'Oranges', 5680);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-04 16:42:48', 'out', 'T-96855', 'C-0794677,C-0258544', 4942, 1874, 1081, 'Oranges', 2948);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-05 23:54:10', 'none', 'T-14732', 'C-0477829,C-0894160,C-0360359,C-0625825', 7531, 1787, 1225, 'Oranges', 8455);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-02 04:58:06', 'none', 'T-63813', 'C-0625825,C-0647344', 5718, 1970, 1408, 'Bananas', 3217);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-15 10:42:34', 'none', 'T-27857', 'C-0894574,C-0625825,C-0745069,C-0867487', 7085, 1397, 1366, 'Grapes', 8375);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-15 10:46:47', 'none', 'T-75930', 'C-0290725', 4822, 2445, 903, 'Mangoes', 2914);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-11 06:07:14', 'none', 'T-89974', 'C-0169739,C-0997392,C-0212527', 6103, 2251, 1101, 'Oranges', 1737);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 02:40:30', 'in', 'T-83381', 'C-0722860,C-0949899,C-0794677,C-0615348,C-0447944', 9449, 2444, 1936, 'Grapes', 1781);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-07 09:28:49', 'in', 'T-48947', 'C-0653112', 4377, 1873, 1941, 'Grapes', 2635);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-08 13:10:26', 'out', 'T-25929', 'C-0723848,C-0477829,C-0258544', 6386, 2224, 501, 'Mangoes', 4888);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-15 14:25:25', 'out', 'T-41801', 'C-0653112,C-0894574,C-0898519,C-0258544,C-0360359', 8167, 1981, 1027, 'Mangoes', 3169);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-05 14:09:03', 'in', 'T-56931', 'C-0997392', 4762, 1833, 1576, 'Oranges', 2599);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-10 21:18:53', 'out', 'T-86369', 'C-0813811,C-0997392,C-0722860,C-0447944', 7586, 1256, 1727, 'Grapes', 4882);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-05 06:13:41', 'out', 'T-19390', 'C-0535215', 4758, 2387, 1682, 'Oranges', 4524);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-14 18:58:17', 'in', 'T-64418', 'C-0625825,C-0258544,C-0451407', 5802, 1413, 872, 'Apples', 1417);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 05:17:29', 'out', 'T-92677', 'C-0535215,C-0477829,C-0508382,C-0211080,C-0259857', 7987, 1939, 1339, 'Oranges', 8065);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 03:18:36', 'in', 'T-25959', 'C-0535215,C-0745069,C-0949899,C-0555979,C-0813811', 9464, 2253, 1798, 'Apples', 2767);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-11 12:55:54', 'in', 'T-76472', 'C-0451407,C-0103679,C-0894682,C-0936917', 7209, 2474, 1412, 'Oranges', 7853);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-14 20:36:49', 'none', 'T-56506', 'C-0936917,C-0290725,C-0894160,C-0723848', 7394, 1778, 1330, 'Oranges', 9417);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-08 23:17:55', 'in', 'T-81098', 'C-0576278,C-0212527,C-0451407,C-0894574,C-0577318', 6672, 1013, 1224, 'Apples', 8173);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-05 08:08:03', 'out', 'T-41689', 'C-0722860,C-0360359', 4634, 1107, 797, 'Apples', 9420);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-14 15:52:06', 'in', 'T-26681', 'C-0894682,C-0745069,C-0258544,C-0447944', 7875, 2999, 500, 'Oranges', 2034);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 02:53:44', 'out', 'T-27138', 'C-0615348,C-0111995,C-0259857,C-0723848', 6741, 1863, 617, 'Oranges', 9251);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-13 03:07:06', 'in', 'T-93134', 'C-0290725,C-0894682,C-0508382', 6043, 1408, 1474, 'Bananas', 5605);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 18:44:20', 'out', 'T-22155', 'C-0894574,C-0722860,C-0508382,C-0781208', 8301, 1445, 1944, 'Grapes', 2518);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-13 07:46:36', 'out', 'T-99510', 'C-0576278,C-0794677,C-0259857,C-0867487,C-0949899', 7556, 1877, 1275, 'Mangoes', 5610);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-06 02:32:34', 'out', 'T-75838', 'C-0615348,C-0903812', 3597, 1225, 943, 'Oranges', 3309);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-10 18:19:09', 'out', 'T-20311', 'C-0480555,C-0360359,C-0794677,C-0535215', 6322, 1800, 851, 'Mangoes', 3888);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-03 15:44:31', 'out', 'T-62441', 'C-0907080,C-0577318,C-0576278,C-0722860', 7781, 2668, 1261, 'Grapes', 1856);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-02 21:04:57', 'out', 'T-56934', 'C-0949899', 4809, 2424, 1094, 'Apples', 5784);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-14 02:49:52', 'none', 'T-71974', 'C-0867487,C-0447944,C-0111995,C-0813811', 7962, 2091, 1994, 'Apples', 9926);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-06 10:26:04', 'in', 'T-53564', 'C-0894682,C-0103679', 5994, 2735, 1958, 'Grapes', 5785);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-15 14:22:26', 'in', 'T-51105', 'C-0918591,C-0923132,C-0480555,C-0690183,C-0723848', 7825, 1569, 919, 'Oranges', 1293);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-14 01:30:15', 'none', 'T-45043', 'C-0907080,C-0259857', 5944, 2375, 1781, 'Bananas', 6600);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-10 18:30:14', 'out', 'T-98817', 'C-0212527,C-0903812,C-0722514,C-0287536', 5937, 1674, 927, 'Oranges', 2636);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-02 13:28:06', 'in', 'T-17228', 'C-0212527,C-0211080,C-0451407', 5311, 1879, 1187, 'Bananas', 3613);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-10 17:39:19', 'none', 'T-12304', 'C-0784016', 3909, 1618, 1394, 'Oranges', 5135);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-11 06:58:36', 'in', 'T-96084', 'C-0745069,C-0529566', 5708, 2671, 786, 'Grapes', 8260);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-08 08:47:44', 'in', 'T-19137', 'C-0447944', 3938, 1462, 1429, 'Mangoes', 3054);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-11 18:12:13', 'out', 'T-84960', 'C-0949899,C-0781208,C-0653112,C-0625825,C-0535215', 8904, 2656, 990, 'Apples', 5514);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-07 23:27:31', 'in', 'T-32422', 'C-0949899,C-0907080,C-0508382', 5081, 1312, 787, 'Grapes', 4983);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-13 03:34:48', 'in', 'T-55325', 'C-0723848,C-0360359', 6172, 2289, 1450, 'Mangoes', 9805);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-06 06:45:28', 'in', 'T-96595', 'C-0952882,C-0647344', 4578, 1475, 731, 'Grapes', 9253);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-06 23:23:53', 'none', 'T-61397', 'C-0280066,C-0555979,C-0625825,C-0781208,C-0577318', 10388, 2258, 1817, 'Grapes', 6624);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-05 20:37:11', 'out', 'T-52324', 'C-0952882', 4583, 2104, 1128, 'Grapes', 1313);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-08 01:12:36', 'out', 'T-85653', 'C-0952882,C-0690183,C-0211080,C-0813811', 9072, 2902, 1960, 'Grapes', 8873);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-14 13:23:14', 'out', 'T-20788', 'C-0615348,C-0923132,C-0867487,C-0794677,C-0784016', 5599, 1097, 996, 'Apples', 1522);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-03 11:30:28', 'out', 'T-96334', 'C-0287536,C-0997392,C-0555979,C-0723848,C-0894160', 7131, 1493, 603, 'Mangoes', 9372);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-06 11:27:43', 'out', 'T-97757', 'C-0903812', 3485, 1715, 1129, 'Apples', 7997);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-09 15:12:23', 'none', 'T-51006', 'C-0550343,C-0280066,C-0211080,C-0555979', 6215, 1282, 670, 'Grapes', 2183);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-11 18:25:00', 'out', 'T-15667', 'C-0550343,C-0625825,C-0451407,C-0287536', 7018, 2220, 1259, 'Bananas', 5741);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-07 23:39:56', 'none', 'T-85067', 'C-0615348,C-0784016,C-0722514,C-0918591,C-0529566', 10135, 2802, 1735, 'Oranges', 6829);
INSERT INTO `transactions` (`datetime`, `direction`, `truck`, `containers`, `bruto`, `truckTara`, `neto`, `produce`, `session_id`) VALUES ('2024-03-13 10:09:40', 'out', 'T-95447', 'C-0212527,C-0936917,C-0722514,C-0907080,C-0923132', 7321, 1930, 787, 'Grapes', 5652);
