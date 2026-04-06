-- ================================================================
--  SMART EVACUATION NAVIGATION SYSTEM
--  SQL Server (T-SQL)  |  Physical Implementation
-- ================================================================

USE SmartEvacuationDB;
GO

-- CHAPTER 8 : STORED PROCEDURES
-- ================================================================

-- SP 01: Register a new building
CREATE OR ALTER PROCEDURE sp_register_building
    @p_name     VARCHAR(150),
    @p_address  VARCHAR(255),
    @p_type     VARCHAR(80),
    @p_floors   INT
AS
BEGIN
    INSERT INTO BUILDING (building_name, address, building_type, total_floors)
    VALUES (@p_name, @p_address, @p_type, @p_floors);
    SELECT SCOPE_IDENTITY() AS new_building_id;
END;
GO

-- SP 02: Add a floor to a building
CREATE OR ALTER PROCEDURE sp_add_floor
    @p_building_id  INT,
    @p_floor_number INT,
    @p_map_ref      VARCHAR(120),
    @p_height       DECIMAL(5,2)
AS
BEGIN
    INSERT INTO FLOOR (building_id, floor_number, map_reference, height_meters)
    VALUES (@p_building_id, @p_floor_number, @p_map_ref, @p_height);
    SELECT SCOPE_IDENTITY() AS new_floor_id;
END;
GO

-- SP 03: Register a new incident
CREATE OR ALTER PROCEDURE sp_register_incident
    @p_building_id  INT,
    @p_type         VARCHAR(80),
    @p_severity     VARCHAR(10),
    @p_start_time   DATETIME,
    @p_description  NVARCHAR(MAX)
AS
BEGIN
    INSERT INTO INCIDENT (building_id, incident_type, severity_level, start_time, status, description)
    VALUES (@p_building_id, @p_type, @p_severity, @p_start_time, 'active', @p_description);
    SELECT SCOPE_IDENTITY() AS new_incident_id;
END;
GO

-- SP 04: Resolve an incident
CREATE OR ALTER PROCEDURE sp_resolve_incident
    @p_incident_id INT
AS
BEGIN
    UPDATE INCIDENT
    SET    status   = 'resolved',
           end_time = GETDATE()
    WHERE  incident_id = @p_incident_id
    AND    status      = 'active';

    IF @@ROWCOUNT = 0
        THROW 50004, 'Incident not found or already resolved.', 1;

    SELECT CONCAT('Incident ', CAST(@p_incident_id AS VARCHAR), ' resolved successfully.') AS message;
END;
GO

-- SP 05: Get available emergency exits for a floor
CREATE OR ALTER PROCEDURE sp_get_available_exits
    @p_floor_id INT
AS
BEGIN
    SELECT ep.exit_id, ep.exit_name, ep.exit_type,
           f.floor_number, b.building_name
    FROM   EXIT_POINT ep
    JOIN   FLOOR f    ON ep.floor_id   = f.floor_id
    JOIN   BUILDING b ON f.building_id = b.building_id
    WHERE  ep.floor_id          = @p_floor_id
    AND    ep.status            = 'available'
    AND    ep.is_emergency_exit = 1;
END;
GO

-- SP 06: Generate an evacuation route
CREATE OR ALTER PROCEDURE sp_generate_route
    @p_incident_id INT,
    @p_user_id     INT,
    @p_start_floor INT,
    @p_dest_exit   INT
AS
BEGIN
    INSERT INTO EVACUATION_ROUTE (incident_id, user_id, start_floor_id, destination_exit_id, route_status)
    VALUES (@p_incident_id, @p_user_id, @p_start_floor, @p_dest_exit, 'generated');
    SELECT SCOPE_IDENTITY() AS new_route_id;
END;
GO

-- SP 07: Add a step to an evacuation route
CREATE OR ALTER PROCEDURE sp_add_route_step
    @p_route_id    INT,
    @p_step_number INT,
    @p_floor_id    INT,
    @p_zone_id     INT,
    @p_instruction NVARCHAR(MAX)
AS
BEGIN
    INSERT INTO ROUTE_STEP (route_id, step_number, floor_id, zone_id, instruction_text)
    VALUES (@p_route_id, @p_step_number, @p_floor_id, @p_zone_id, @p_instruction);
END;
GO

-- SP 08: Log a beacon detection event
CREATE OR ALTER PROCEDURE sp_log_location
    @p_user_id   INT,
    @p_beacon_id INT,
    @p_floor_id  INT,
    @p_zone_id   INT
AS
BEGIN
    INSERT INTO USER_LOCATION (user_id, beacon_id, floor_id, zone_id, detected_at)
    VALUES (@p_user_id, @p_beacon_id, @p_floor_id, @p_zone_id, GETDATE());
    SELECT SCOPE_IDENTITY() AS new_location_id;
END;
GO

-- SP 09: Get evacuation history for a user
CREATE OR ALTER PROCEDURE sp_get_user_history
    @p_user_id INT
AS
BEGIN
    SELECT er.route_id,
           b.building_name,
           i.incident_type,
           i.severity_level,
           f.floor_number  AS start_floor,
           ep.exit_name    AS destination_exit,
           er.route_status,
           er.created_at
    FROM   EVACUATION_ROUTE er
    JOIN   INCIDENT i    ON er.incident_id         = i.incident_id
    JOIN   BUILDING b    ON i.building_id          = b.building_id
    JOIN   FLOOR f       ON er.start_floor_id      = f.floor_id
    JOIN   EXIT_POINT ep ON er.destination_exit_id = ep.exit_id
    WHERE  er.user_id = @p_user_id
    ORDER  BY er.created_at DESC;
END;
GO

-- SP 10: Get all active incidents
CREATE OR ALTER PROCEDURE sp_get_active_incidents
AS
BEGIN
    SELECT i.incident_id, b.building_name, b.address,
           i.incident_type, i.severity_level,
           i.start_time, i.description
    FROM   INCIDENT i
    JOIN   BUILDING b ON i.building_id = b.building_id
    WHERE  i.status = 'active'
    ORDER  BY i.severity_level DESC, i.start_time;
END;
GO

-- SP 11: Get statistics for a building
CREATE OR ALTER PROCEDURE sp_get_building_stats
    @p_building_id INT
AS
BEGIN
    SELECT b.building_name, b.building_type,
        (SELECT COUNT(*) FROM FLOOR    WHERE building_id = b.building_id) AS floors,
        (SELECT COUNT(*) FROM INCIDENT WHERE building_id = b.building_id) AS incidents,
        (SELECT COUNT(*) FROM EMPLOYEE WHERE building_id = b.building_id) AS employees,
        (SELECT COUNT(*) FROM BEACON bc
            JOIN FLOOR f ON bc.floor_id = f.floor_id
            WHERE f.building_id = b.building_id)                          AS beacons,
        (SELECT COUNT(*) FROM EXIT_POINT ep
            JOIN FLOOR f ON ep.floor_id = f.floor_id
            WHERE f.building_id = b.building_id)                          AS exits
    FROM   BUILDING b
    WHERE  b.building_id = @p_building_id;
END;
GO

-- SP 12: Assign a beacon to a floor
CREATE OR ALTER PROCEDURE sp_assign_beacon
    @p_floor_id    INT,
    @p_zone_id     INT,
    @p_uuid        VARCHAR(36),
    @p_major       INT,
    @p_minor       INT,
    @p_install     DATE
AS
BEGIN
    IF EXISTS (SELECT 1 FROM BEACON WHERE uuid = @p_uuid)
        THROW 50006, 'Error BR-06: Beacon UUID must be globally unique.', 1;

    INSERT INTO BEACON (floor_id, zone_id, uuid, major_value, minor_value, install_date, status)
    VALUES (@p_floor_id, @p_zone_id, @p_uuid, @p_major, @p_minor, @p_install, 'active');
    SELECT SCOPE_IDENTITY() AS new_beacon_id;
END;
GO


-- ================================================================