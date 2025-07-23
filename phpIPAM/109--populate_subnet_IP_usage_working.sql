--- below script randomly populates Resrved, Used, DHCP & Offline tags on random 5-10 IPs.

MariaDB [phpipam]> DELIMITER $$
MariaDB [phpipam]>
MariaDB [phpipam]> CREATE PROCEDURE populate_random_ips()
-> BEGIN
->     DECLARE done INT DEFAULT FALSE;
->     DECLARE v_subnetId INT;
->     DECLARE v_subnet INT UNSIGNED;
->     DECLARE v_mask INT;
->
->     DECLARE cur CURSOR FOR SELECT id, subnet, mask FROM subnets;
->     DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
->
->     OPEN cur;
->
VALUES (v_subnetId, @rand_ip, 'Auto-generated', @state);

SET @inserted = @inserted + 1;
END IF;
END WHILE;

END LOOP;

CLOSE cur;
END$$

DELIMITER ;
->     read_loop: LOOP
->         FETCH cur INTO v_subnetId, v_subnet, v_mask;
->         IF done THEN
->             LEAVE read_loop;
->         END IF;
->
->         -- Calculate usable IP range
->         SET @network = v_subnet;
->         SET @maskbits = v_mask;
->         SET @hostbits = 32 - @maskbits;
->         SET @num_ips = POW(2, @hostbits);
->         SET @first_ip = @network + 1;
->         SET @last_ip = @network + @num_ips - 2;
->
->         -- Determine random counts
->         SET @used_count = FLOOR(10 + RAND() * 21);       -- 10-30
->         SET @reserved_count = FLOOR(5 + RAND() * 6);     -- 5-10
->         SET @offline_count = FLOOR(5 + RAND() * 6);      -- 5-10
->         SET @dhcp_count = FLOOR(5 + RAND() * 6);         -- 5-10
->
->         -- Helper variables
->         SET @inserted = 0;
->
->         WHILE @inserted < (@used_count + @reserved_count + @offline_count + @dhcp_count) DO
->             SET @rand_ip = FLOOR(@first_ip + (RAND() * (@last_ip - @first_ip + 1)));
->
->             -- Check if IP already exists in ipaddresses
->             SET @exists = (SELECT COUNT(*) FROM ipaddresses WHERE subnetId = v_subnetId AND ip_addr = @rand_ip);
->
->             IF @exists = 0 THEN
->                 -- Decide state based on current insertion count
->                 IF @inserted < @used_count THEN
->                     SET @state = 0;
->                 ELSEIF @inserted < @used_count + @reserved_count THEN
->                     SET @state = 1;
->                 ELSEIF @inserted < @used_count + @reserved_count + @offline_count THEN
->                     SET @state = 2;
->                 ELSE
->                     SET @state = 3;
->                 END IF;
->
->                 -- Insert the IP
->                 INSERT INTO ipaddresses (subnetId, ip_addr, description, state)
->                 VALUES (v_subnetId, @rand_ip, 'Auto-generated', @state);
->
->                 SET @inserted = @inserted + 1;
->             END IF;
->         END WHILE;
->
->     END LOOP;
->
->     CLOSE cur;
-> END$$
Query OK, 0 rows affected (0.019 sec)

MariaDB [phpipam]>
MariaDB [phpipam]> DELIMITER ;
MariaDB [phpipam]> CALL populate_random_ips();
Query OK, 11859 rows affected (33.308 sec)

MariaDB [phpipam]>