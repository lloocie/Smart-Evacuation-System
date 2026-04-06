-- ================================================================
--  SMART EVACUATION NAVIGATION SYSTEM
--  SQL Server (T-SQL)  |  Physical Implementation
-- ================================================================

USE SmartEvacuationDB;
GO

-- CHAPTER 5 : VIEWS
-- ================================================================

-- View 1: vw_active_incidents
CREATE OR ALTER VIEW vw_active_incidents AS
SELECT i.incident_id, b.building_name, b.address,
       i.incident_type, i.severity_level,
       i.start_time, i.description
FROM   INCIDENT i
JOIN   BUILDING b ON i.building_id = b.building_id
WHERE  i.status = 'active';
GO

-- View 2: vw_available_emergency_exits
CREATE OR ALTER VIEW vw_available_emergency_exits AS
SELECT ep.exit_id, ep.exit_name, ep.exit_type,
       f.floor_id, f.floor_number, b.building_name
FROM   EXIT_POINT ep
JOIN   FLOOR f    ON ep.floor_id   = f.floor_id
JOIN   BUILDING b ON f.building_id = b.building_id
WHERE  ep.is_emergency_exit = 1
AND    ep.status = 'available';
GO

-- View 3: vw_evacuation_details
CREATE OR ALTER VIEW vw_evacuation_details AS
SELECT er.route_id,
       ua.full_name    AS evacuee,
       b.building_name,
       i.incident_type,
       i.severity_level,
       f.floor_number  AS start_floor,
       ep.exit_name    AS destination_exit,
       er.route_status,
       er.created_at,
       rs.step_number,
       rs.instruction_text
FROM   EVACUATION_ROUTE er
JOIN   USER_ACCOUNT ua   ON er.user_id             = ua.user_id
JOIN   INCIDENT i         ON er.incident_id         = i.incident_id
JOIN   BUILDING b         ON i.building_id          = b.building_id
JOIN   FLOOR f            ON er.start_floor_id      = f.floor_id
JOIN   EXIT_POINT ep      ON er.destination_exit_id = ep.exit_id
LEFT   JOIN ROUTE_STEP rs ON er.route_id            = rs.route_id;
GO

-- View 4: vw_beacon_summary
CREATE OR ALTER VIEW vw_beacon_summary AS
SELECT bc.beacon_id, bc.uuid, bc.status, bc.install_date,
       f.floor_number, b.building_name,
       COALESCE(z.zone_name, 'Unassigned') AS zone_name
FROM   BEACON bc
JOIN   FLOOR f     ON bc.floor_id  = f.floor_id
JOIN   BUILDING b  ON f.building_id = b.building_id
LEFT   JOIN ZONE z ON bc.zone_id   = z.zone_id;
GO

-- View 5: vw_employee_directory
CREATE OR ALTER VIEW vw_employee_directory AS
SELECT e.employee_id, ua.full_name, ua.email,
       e.job_title, e.department, e.salary,
       b.building_name,
       COALESCE(z.zone_name, 'N/A') AS zone_name,
       e.shift_start, e.shift_end, e.status
FROM   EMPLOYEE e
JOIN   USER_ACCOUNT ua ON e.user_id     = ua.user_id
JOIN   BUILDING b       ON e.building_id = b.building_id
LEFT   JOIN ZONE z      ON e.zone_id    = z.zone_id;
GO

-- View 6: vw_location_audit
CREATE OR ALTER VIEW vw_location_audit AS
SELECT ul.location_id, ua.full_name, ua.email,
       b.building_name, f.floor_number,
       COALESCE(z.zone_name, 'N/A') AS zone_name,
       bc.uuid AS beacon_uuid, ul.detected_at
FROM   USER_LOCATION ul
JOIN   USER_ACCOUNT ua ON ul.user_id    = ua.user_id
JOIN   BEACON bc        ON ul.beacon_id = bc.beacon_id
JOIN   FLOOR f          ON ul.floor_id  = f.floor_id
JOIN   BUILDING b       ON f.building_id = b.building_id
LEFT   JOIN ZONE z      ON ul.zone_id   = z.zone_id;
GO

-- View 7: vw_incident_summary
CREATE OR ALTER VIEW vw_incident_summary AS
SELECT b.building_id, b.building_name, b.building_type,
       COUNT(i.incident_id)                                      AS total_incidents,
       SUM(CASE WHEN i.status = 'active'   THEN 1 ELSE 0 END)   AS active_count,
       SUM(CASE WHEN i.status = 'resolved' THEN 1 ELSE 0 END)   AS resolved_count,
       SUM(CASE WHEN i.severity_level = 'critical' THEN 1 ELSE 0 END) AS critical_count
FROM   BUILDING b
LEFT   JOIN INCIDENT i ON b.building_id = i.building_id
GROUP  BY b.building_id, b.building_name, b.building_type;
GO


-- ================================================================