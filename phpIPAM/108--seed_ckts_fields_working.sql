MariaDB [phpipam]> -- Update locations with description, address, lat, long
MariaDB [phpipam]> UPDATE locations SET
->     description = name,
->     address = CASE id
->         WHEN 1 THEN '123 East St, New York, USA'
->         WHEN 2 THEN '456 West Ave, San Francisco, USA'
->         WHEN 3 THEN '789 Hauptstrasse, Berlin, Germany'
->         WHEN 4 THEN 'Plot 32, Bangalore, India'
->         WHEN 5 THEN 'Shinjuku, Tokyo, Japan'
->         WHEN 6 THEN 'One Raffles Place, Singapore'
->         WHEN 7 THEN '123 Collins St, Melbourne, Australia'
->         WHEN 8 THEN 'Gangnam-gu, Seoul, South Korea'
->         WHEN 9 THEN 'Central, Hong Kong'
->         WHEN 10 THEN 'Via Roma 15, Milan, Italy'
->         WHEN 11 THEN 'Calle Gran Via, Madrid, Spain'
->         WHEN 12 THEN 'Rue de Rivoli, Paris, France'
->         WHEN 13 THEN 'Prinsengracht, Amsterdam, Netherlands'
->         WHEN 14 THEN 'Sveavägen 45, Stockholm, Sweden'
->         WHEN 15 THEN 'Karl Johans gate, Oslo, Norway'
->         WHEN 16 THEN 'Ulica Marszalkowska, Warsaw, Poland'
->         WHEN 17 THEN 'King St W, Toronto, Canada'
->         WHEN 18 THEN 'Paseo de la Reforma, Mexico City, Mexico'
->         WHEN 19 THEN 'Avenida Paulista, São Paulo, Brazil'
->         WHEN 20 THEN 'Avenida Santa Fe, Buenos Aires, Argentina'
->         WHEN 21 THEN 'Alameda, Santiago, Chile'
->         WHEN 22 THEN 'Av. Arequipa, Lima, Peru'
->         WHEN 23 THEN 'Calle 93, Bogota, Colombia'
->         WHEN 24 THEN 'Bulevar Artigas, Montevideo, Uruguay'
->         ELSE address
->     END,
->     lat = CASE id
->         WHEN 1 THEN '40.7128'
->         WHEN 2 THEN '37.7749'
->         WHEN 3 THEN '52.5200'
->         WHEN 4 THEN '12.9716'
->         WHEN 5 THEN '35.6895'
->         WHEN 6 THEN '1.3521'
->         WHEN 7 THEN '-37.8136'
->         WHEN 8 THEN '37.5665'
->         WHEN 9 THEN '22.3193'
->         WHEN 10 THEN '45.4642'
->         WHEN 11 THEN '40.4168'
->         WHEN 12 THEN '48.8566'
->         WHEN 13 THEN '52.3676'
->         WHEN 14 THEN '59.3293'
->         WHEN 15 THEN '59.9139'
->         WHEN 16 THEN '52.2297'
->         WHEN 17 THEN '43.6532'
->         WHEN 18 THEN '19.4326'
->         WHEN 19 THEN '-23.5505'
->         WHEN 20 THEN '-34.6037'
->         WHEN 21 THEN '-33.4489'
->         WHEN 22 THEN '-12.0464'
->         WHEN 23 THEN '4.7110'
->         WHEN 24 THEN '-34.9011'
->         ELSE lat
->     END,
->     `long` = CASE id
->         WHEN 1 THEN '-74.0060'
->         WHEN 2 THEN '-122.4194'
->         WHEN 3 THEN '13.4050'
->         WHEN 4 THEN '77.5946'
->         WHEN 5 THEN '139.6917'
->         WHEN 6 THEN '103.8198'
->         WHEN 7 THEN '144.9631'
->         WHEN 8 THEN '126.9780'
->         WHEN 9 THEN '114.1694'
->         WHEN 10 THEN '9.1900'
->         WHEN 11 THEN '-3.7038'
->         WHEN 12 THEN '2.3522'
->         WHEN 13 THEN '4.9041'
->         WHEN 14 THEN '18.0686'
->         WHEN 15 THEN '10.7522'
->         WHEN 16 THEN '21.0122'
->         WHEN 17 THEN '-79.3832'
->         WHEN 18 THEN '-99.1332'
->         WHEN 19 THEN '-46.6333'
->         WHEN 20 THEN '-58.3816'
->         WHEN 21 THEN '-70.6693'
->         WHEN 22 THEN '-77.0428'
->         WHEN 23 THEN '-74.0721'
->         WHEN 24 THEN '-56.1645'
->         ELSE `long`
->     END;
Query OK, 24 rows affected (0.014 sec)
Rows matched: 24  Changed: 24  Warnings: 0

MariaDB [phpipam]>
MariaDB [phpipam]>
MariaDB [phpipam]> SELECT id, name, description, address, lat, `long` FROM locations ORDER BY id;
+----+------------------+------------------+-------------------------------------------+----------+-----------+
| id | name             | description      | address                                   | lat      | long      |
+----+------------------+------------------+-------------------------------------------+----------+-----------+
|  1 | AMER-East        | AMER-East        | 123 East St, New York, USA                | 40.7128  | -74.0060  |
|  2 | AMER-West        | AMER-West        | 456 West Ave, San Francisco, USA          | 37.7749  | -122.4194 |
|  3 | EMEA-Germany     | EMEA-Germany     | 789 Hauptstrasse, Berlin, Germany         | 52.5200  | 13.4050   |
|  4 | AP-India         | AP-India         | Plot 32, Bangalore, India                 | 12.9716  | 77.5946   |
|  5 | AP-Japan         | AP-Japan         | Shinjuku, Tokyo, Japan                    | 35.6895  | 139.6917  |
|  6 | AP-Singapore     | AP-Singapore     | One Raffles Place, Singapore              | 1.3521   | 103.8198  |
|  7 | AP-Australia     | AP-Australia     | 123 Collins St, Melbourne, Australia      | -37.8136 | 144.9631  |
|  8 | AP-SouthKorea    | AP-SouthKorea    | Gangnam-gu, Seoul, South Korea            | 37.5665  | 126.9780  |
|  9 | AP-HongKong      | AP-HongKong      | Central, Hong Kong                        | 22.3193  | 114.1694  |
| 10 | EMEA-Italy       | EMEA-Italy       | Via Roma 15, Milan, Italy                 | 45.4642  | 9.1900    |
| 11 | EMEA-Spain       | EMEA-Spain       | Calle Gran Via, Madrid, Spain             | 40.4168  | -3.7038   |
| 12 | EMEA-France      | EMEA-France      | Rue de Rivoli, Paris, France              | 48.8566  | 2.3522    |
| 13 | EMEA-Netherlands | EMEA-Netherlands | Prinsengracht, Amsterdam, Netherlands     | 52.3676  | 4.9041    |
| 14 | EMEA-Sweden      | EMEA-Sweden      | Sveavägen 45, Stockholm, Sweden           | 59.3293  | 18.0686   |
| 15 | EMEA-Norway      | EMEA-Norway      | Karl Johans gate, Oslo, Norway            | 59.9139  | 10.7522   |
| 16 | EMEA-Poland      | EMEA-Poland      | Ulica Marszalkowska, Warsaw, Poland       | 52.2297  | 21.0122   |
| 17 | AMER-Canada      | AMER-Canada      | King St W, Toronto, Canada                | 43.6532  | -79.3832  |
| 18 | AMER-Mexico      | AMER-Mexico      | Paseo de la Reforma, Mexico City, Mexico  | 19.4326  | -99.1332  |
| 19 | AMER-Brazil      | AMER-Brazil      | Avenida Paulista, São Paulo, Brazil       | -23.5505 | -46.6333  |
| 20 | AMER-Argentina   | AMER-Argentina   | Avenida Santa Fe, Buenos Aires, Argentina | -34.6037 | -58.3816  |
| 21 | AMER-Chile       | AMER-Chile       | Alameda, Santiago, Chile                  | -33.4489 | -70.6693  |
| 22 | AMER-Peru        | AMER-Peru        | Av. Arequipa, Lima, Peru                  | -12.0464 | -77.0428  |
| 23 | AMER-Colombia    | AMER-Colombia    | Calle 93, Bogota, Colombia                | 4.7110   | -74.0721  |
| 24 | AMER-Uruguay     | AMER-Uruguay     | Bulevar Artigas, Montevideo, Uruguay      | -34.9011 | -56.1645  |
+----+------------------+------------------+-------------------------------------------+----------+-----------+
24 rows in set (0.000 sec)

MariaDB [phpipam]>