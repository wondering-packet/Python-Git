-- assumes you already have the custom fields created
-- verify using: DESCRIBE circuits;

MariaDB [phpipam]> SELECT id, name FROM locations;
+----+------------------+
| id | name             |
+----+------------------+
|  1 | AMER-East        |
|  2 | AMER-West        |
|  3 | EMEA-Germany     |
|  4 | AP-India         |
|  5 | AP-Japan         |
|  6 | AP-Singapore     |
|  7 | AP-Australia     |
|  8 | AP-SouthKorea    |
|  9 | AP-HongKong      |
| 10 | EMEA-Italy       |
| 11 | EMEA-Spain       |
| 12 | EMEA-France      |
| 13 | EMEA-Netherlands |
| 14 | EMEA-Sweden      |
| 15 | EMEA-Norway      |
| 16 | EMEA-Poland      |
| 17 | AMER-Canada      |
| 18 | AMER-Mexico      |
| 19 | AMER-Brazil      |
| 20 | AMER-Argentina   |
| 21 | AMER-Chile       |
| 22 | AMER-Peru        |
| 23 | AMER-Colombia    |
| 24 | AMER-Uruguay     |
+----+------------------+
24 rows in set (0.000 sec)

MariaDB [phpipam]> SELECT id, name FROM circuitProviders;
+----+------------+
| id | name       |
+----+------------+
|  1 | AT&T       |
|  2 | Verizon    |
|  3 | Chromecast |
+----+------------+
3 rows in set (0.000 sec)

MariaDB [phpipam]> -- Initialize randomization populate
MariaDB [phpipam]> SET @populate := UNIX_TIMESTAMP();
Query OK, 0 rows affected (0.000 sec)

MariaDB [phpipam]>
MariaDB [phpipam]> -- Insert 30 random physical circuits into phpIPAM circuits table
MariaDB [phpipam]> INSERT INTO circuits
-> (
->     cid,
->     provider,
->     status,
->     capacity,
->     custom_Contract_End_Date,
->     custom_MRC,
->     `custom_Account Number`,
->     location1,
->     location2
-> )
-> SELECT
->     CONCAT('CIR-', FLOOR(RAND(@populate + t1.id) * 1000000)), -- random circuit ID
->     ELT(FLOOR(1 + (RAND(@populate + t1.id + 100) * 3)), 1, 2, 3), -- provider id: AT&T, Verizon, Chromecast
->     ELT(FLOOR(1 + (RAND(@populate + t1.id + 200) * 3)), 'Active', 'Inactive', 'Reserved'), -- status
->     ELT(FLOOR(1 + (RAND(@populate + t1.id + 300) * 3)), '500', '1000', '10000'), -- capacity
->     DATE_ADD(CURDATE(), INTERVAL FLOOR(RAND(@populate + t1.id + 400) * 365 * 5) DAY), -- random future date
->     CONCAT('$', FLOOR(20 + (RAND(@populate + t1.id + 500) * 481))), -- $20 - $500
->     FLOOR(10000 + (RAND(@populate + t1.id + 600) * 99999999)), -- random 5-10 digit account number
->     ELT(FLOOR(1 + (RAND(@populate + t1.id + 700) * 24)),
->         1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
->         13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), -- location1
->     ELT(FLOOR(1 + (RAND(@populate + t1.id + 800) * 24)),
->         1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
->         13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24) -- location2
-> FROM (
->     SELECT @row := @row + 1 AS id
->     FROM (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
->           UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) t1,
->          (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2) t2,
->          (SELECT @row := 0) t0
->     LIMIT 30
-> ) t1;
Query OK, 30 rows affected (0.016 sec)
Records: 30  Duplicates: 0  Warnings: 0

MariaDB [phpipam]> SELECT id, cid, provider, status, capacity, custom_Contract_End_Date, custom_MRC, `custom_Account Number`, location1, location2
-> FROM circuits
-> ORDER BY id DESC
-> LIMIT 30;
+----+------------+----------+----------+----------+--------------------------+------------+-----------------------+-----------+-----------+
| id | cid        | provider | status   | capacity | custom_Contract_End_Date | custom_MRC | custom_Account Number | location1 | location2 |
+----+------------+----------+----------+----------+--------------------------+------------+-----------------------+-----------+-----------+
| 30 | CIR-566706 |        2 | Inactive | 1000     | 2028-10-02               | $336       | 67667235              |        17 |        18 |
| 29 | CIR-316523 |        2 | Inactive | 1000     | 2027-07-04               | $216       | 42648924              |        11 |        12 |
| 28 | CIR-66340  |        1 | Active   | 500      | 2026-04-03               | $95        | 17630613              |         5 |         6 |
| 27 | CIR-816157 |        3 | Reserved | 10000    | 2030-01-01               | $456       | 92612302              |        23 |        24 |
| 26 | CIR-565974 |        2 | Inactive | 1000     | 2028-10-01               | $336       | 67593991              |        17 |        18 |
| 25 | CIR-315791 |        2 | Inactive | 1000     | 2027-07-02               | $215       | 42575681              |        11 |        12 |
| 24 | CIR-65608  |        1 | Active   | 500      | 2026-04-02               | $95        | 17557370              |         5 |         6 |
| 23 | CIR-815425 |        3 | Reserved | 10000    | 2029-12-30               | $456       | 92539058              |        23 |        24 |
| 22 | CIR-565241 |        2 | Inactive | 1000     | 2028-09-30               | $335       | 67520748              |        17 |        18 |
| 21 | CIR-315058 |        2 | Inactive | 1000     | 2027-07-01               | $215       | 42502437              |        11 |        12 |
| 20 | CIR-64875  |        1 | Active   | 500      | 2026-04-01               | $95        | 17484126              |         5 |         6 |
| 19 | CIR-814692 |        3 | Reserved | 10000    | 2029-12-29               | $455       | 92465814              |        23 |        24 |
| 18 | CIR-564509 |        2 | Inactive | 1000     | 2028-09-28               | $335       | 67447504              |        17 |        18 |
| 17 | CIR-314326 |        1 | Inactive | 1000     | 2027-06-30               | $215       | 42429193              |        11 |        12 |
| 16 | CIR-64143  |        1 | Active   | 500      | 2026-03-30               | $94        | 17410882              |         5 |         6 |
| 15 | CIR-813960 |        3 | Reserved | 10000    | 2029-12-28               | $455       | 92392571              |        23 |        24 |
| 14 | CIR-563777 |        2 | Inactive | 1000     | 2028-09-27               | $335       | 67374260              |        17 |        18 |
| 13 | CIR-313593 |        1 | Inactive | 1000     | 2027-06-28               | $214       | 42355949              |        11 |        12 |
| 12 | CIR-63410  |        1 | Active   | 500      | 2026-03-29               | $94        | 17337639              |         5 |         6 |
| 11 | CIR-813227 |        3 | Reserved | 10000    | 2029-12-26               | $455       | 92319327              |        23 |        24 |
| 10 | CIR-563044 |        2 | Inactive | 1000     | 2028-09-26               | $334       | 67301016              |        17 |        18 |
|  9 | CIR-312861 |        1 | Inactive | 1000     | 2027-06-27               | $214       | 42282706              |        11 |        12 |
|  8 | CIR-62678  |        1 | Active   | 500      | 2026-03-28               | $94        | 17264395              |         5 |         6 |
|  7 | CIR-812495 |        3 | Reserved | 10000    | 2029-12-25               | $454       | 92246084              |        23 |        24 |
|  6 | CIR-562312 |        2 | Inactive | 1000     | 2028-09-24               | $334       | 67227773              |        17 |        18 |
|  5 | CIR-312129 |        1 | Inactive | 1000     | 2027-06-26               | $214       | 42209462              |        11 |        12 |
|  4 | CIR-61946  |        1 | Active   | 500      | 2026-03-26               | $93        | 17191151              |         5 |         6 |
|  3 | CIR-811762 |        3 | Reserved | 10000    | 2029-12-24               | $454       | 92172840              |        23 |        23 |
|  2 | CIR-561579 |        2 | Inactive | 1000     | 2028-09-23               | $334       | 67154529              |        17 |        17 |
|  1 | CIR-311396 |        1 | Inactive | 1000     | 2027-06-24               | $213       | 42136218              |        11 |        11 |
+----+------------+----------+----------+----------+--------------------------+------------+-----------------------+-----------+-----------+
30 rows in set (0.000 sec)

MariaDB [phpipam]>
MariaDB [phpipam]>