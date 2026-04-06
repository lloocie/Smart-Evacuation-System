-- ================================================================
--  SMART EVACUATION NAVIGATION SYSTEM
--  SQL Server (T-SQL)  |  Physical Implementation
-- ================================================================

USE SmartEvacuationDB;
GO

-- CHAPTER 7 : TRIGGERS
-- ================================================================

-- Trigger 1: Validate beacon belongs to the correct floor
CREATE OR ALTER TRIGGER trg_validate_beacon_floor
ON USER_LOCATION
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (
        SELECT 1 FROM inserted i
        JOIN BEACON b ON i.beacon_id = b.beacon_id
        WHERE b.floor_id <> i.floor_id
    )
    BEGIN
        THROW 50012, 'Error BR-12: Beacon does not belong to this floor.', 1;
        RETURN;
    END
    INSERT INTO USER_LOCATION (user_id, beacon_id, floor_id, zone_id, detected_at)
    SELECT user_id, beacon_id, floor_id, zone_id, detected_at FROM inserted;
END;
GO

-- Trigger 2: Automatically set end_time when incident is resolved
CREATE OR ALTER TRIGGER trg_auto_end_time
ON INCIDENT
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE INCIDENT
    SET    end_time = GETDATE()
    WHERE  incident_id IN (
        SELECT i.incident_id
        FROM   inserted i
        JOIN   deleted d ON i.incident_id = d.incident_id
        WHERE  i.status = 'resolved'
        AND    d.status = 'active'
        AND    i.end_time IS NULL
    );
END;
GO

-- Trigger 3: Validate end_time is after start_time
CREATE OR ALTER TRIGGER trg_check_end_time
ON INCIDENT
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (
        SELECT 1 FROM inserted
        WHERE end_time IS NOT NULL AND end_time <= start_time
    )
    BEGIN
        THROW 50013, 'Error BR-13: end_time must be after start_time.', 1;
        ROLLBACK;
    END;
END;
GO

-- Trigger 4: Prevent duplicate step numbers in the same route
CREATE OR ALTER TRIGGER trg_no_duplicate_step
ON ROUTE_STEP
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (
        SELECT 1 FROM inserted i
        JOIN ROUTE_STEP rs ON i.route_id = rs.route_id
                          AND i.step_number = rs.step_number
    )
    BEGIN
        THROW 50004, 'Error: This step_number already exists for this route.', 1;
        RETURN;
    END;
    INSERT INTO ROUTE_STEP (route_id, step_number, floor_id, zone_id, instruction_text)
    SELECT route_id, step_number, floor_id, zone_id, instruction_text FROM inserted;
END;
GO

-- Trigger 5: Set default route_status to generated on insert
CREATE OR ALTER TRIGGER trg_default_route_status
ON EVACUATION_ROUTE
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO EVACUATION_ROUTE (incident_id, user_id, start_floor_id, destination_exit_id, created_at, route_status)
    SELECT incident_id, user_id, start_floor_id, destination_exit_id, created_at,
           CASE WHEN route_status IS NULL OR route_status = '' THEN 'generated' ELSE route_status END
    FROM inserted;
END;
GO

-- Trigger 6: Block all deletion from INCIDENT
CREATE OR ALTER TRIGGER trg_no_delete_incident
ON INCIDENT
INSTEAD OF DELETE
AS
BEGIN
    THROW 50014, 'Error BR-14: Deleting INCIDENT records is not allowed.', 1;
END;
GO

-- Trigger 7: Block all deletion from EVACUATION_ROUTE
CREATE OR ALTER TRIGGER trg_no_delete_route
ON EVACUATION_ROUTE
INSTEAD OF DELETE
AS
BEGIN
    THROW 50015, 'Error BR-14: Deleting EVACUATION_ROUTE records is not allowed.', 1;
END;
GO

-- Trigger 8: Block all deletion from USER_LOCATION
CREATE OR ALTER TRIGGER trg_no_delete_location
ON USER_LOCATION
INSTEAD OF DELETE
AS
BEGIN
    THROW 50016, 'Error BR-14: Deleting USER_LOCATION records is not allowed.', 1;
END;
GO

-- Trigger 9: Block non-emergency exits when active incident starts
-- Process P4: When an active incident is inserted, all non-emergency
-- exits in that building are set to blocked — BUT only for floors
-- that have at least one available emergency exit (BR Section 1.4).
CREATE OR ALTER TRIGGER trg_block_exits_on_incident
ON INCIDENT
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE EXIT_POINT
    SET    status = 'blocked'
    WHERE  is_emergency_exit = 0
    AND    floor_id IN (
        SELECT f.floor_id
        FROM   FLOOR f
        JOIN   inserted i ON f.building_id = i.building_id
        WHERE  i.status = 'active'
        AND    EXISTS (
            SELECT 1 FROM EXIT_POINT ep2
            WHERE  ep2.floor_id          = f.floor_id
            AND    ep2.is_emergency_exit = 1
            AND    ep2.status            = 'available'
        )
    );
END;
GO


-- ================================================================