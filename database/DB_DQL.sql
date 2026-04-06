-- ================================================================
--  SMART EVACUATION NAVIGATION SYSTEM
--  SQL Server |  Physical Implementation
-- ================================================================

USE SmartEvacuationDB;
GO

-- CHAPTER 4 : DQL - DATA RETRIEVAL QUERIES (33 queries)
-- ================================================================

-- Q01: All active incidents
SELECT * FROM INCIDENT WHERE status = 'active';

-- Q02: All floors in building 1
SELECT * FROM FLOOR WHERE building_id = 1;

-- Q03: All blocked exits
SELECT * FROM EXIT_POINT WHERE status = 'blocked';

-- Q04: All available emergency exits
SELECT * FROM EXIT_POINT
WHERE  is_emergency_exit = 1 AND status = 'available';

-- Q05: All active beacons
SELECT * FROM BEACON WHERE status = 'active';

-- Q06: All admin users
SELECT * FROM USER_ACCOUNT WHERE role = 'admin';

-- Q07: All critical severity incidents
SELECT * FROM INCIDENT WHERE severity_level = 'critical';

-- Q08: All zones on floor 3
SELECT * FROM ZONE WHERE floor_id = 3;

-- Q09: All completed evacuation routes
SELECT * FROM EVACUATION_ROUTE WHERE route_status = 'completed';

-- Q10: All active employees
SELECT * FROM EMPLOYEE WHERE status = 'active';

-- Q11: Building names and addresses only
SELECT building_name, address FROM BUILDING;

-- Q12: User full names and emails only
SELECT full_name, email FROM USER_ACCOUNT;

-- Q13: Beacon UUIDs and install dates only
SELECT uuid, install_date FROM BEACON;

-- Q14: Exit names and types only
SELECT exit_name, exit_type FROM EXIT_POINT;

-- Q15: Incident types and severity levels only
SELECT incident_type, severity_level FROM INCIDENT;

-- Q16: Beacons with floor number and building name
SELECT bc.uuid, f.floor_number, b.building_name
FROM   BEACON bc
JOIN   FLOOR f    ON bc.floor_id   = f.floor_id
JOIN   BUILDING b ON f.building_id = b.building_id;

-- Q17: Evacuation routes with user name and incident type
SELECT ua.full_name, i.incident_type, i.severity_level,
       er.route_status, er.created_at
FROM   EVACUATION_ROUTE er
JOIN   USER_ACCOUNT ua ON er.user_id     = ua.user_id
JOIN   INCIDENT i       ON er.incident_id = i.incident_id;

-- Q18: Route steps with floor number and instruction
SELECT rs.step_number, f.floor_number, rs.instruction_text
FROM   ROUTE_STEP rs
JOIN   EVACUATION_ROUTE er ON rs.route_id = er.route_id
JOIN   FLOOR f             ON rs.floor_id = f.floor_id
ORDER  BY rs.route_id, rs.step_number;

-- Q19: User location history with beacon UUID and building
SELECT ua.full_name, bc.uuid AS beacon_uuid,
       f.floor_number, b.building_name, ul.detected_at
FROM   USER_LOCATION ul
JOIN   USER_ACCOUNT ua ON ul.user_id    = ua.user_id
JOIN   BEACON bc        ON ul.beacon_id = bc.beacon_id
JOIN   FLOOR f          ON ul.floor_id  = f.floor_id
JOIN   BUILDING b       ON f.building_id = b.building_id
ORDER  BY ul.detected_at DESC;

-- Q20: Incidents with building name and address
SELECT i.incident_type, i.severity_level, i.status,
       b.building_name, b.address
FROM   INCIDENT i
JOIN   BUILDING b ON i.building_id = b.building_id;

-- Q21: Employees with user details and building
SELECT ua.full_name, e.job_title, e.department,
       e.salary, b.building_name
FROM   EMPLOYEE e
JOIN   USER_ACCOUNT ua ON e.user_id     = ua.user_id
JOIN   BUILDING b       ON e.building_id = b.building_id;

-- Q22: Exits with floor number, zone name, and building
SELECT ep.exit_name, ep.exit_type, ep.status,
       f.floor_number,
       COALESCE(z.zone_name, 'N/A') AS zone_name,
       b.building_name
FROM   EXIT_POINT ep
JOIN   FLOOR f    ON ep.floor_id   = f.floor_id
JOIN   BUILDING b ON f.building_id = b.building_id
LEFT   JOIN ZONE z ON ep.zone_id   = z.zone_id;

-- Q23: All users - admins and occupants combined (UNION)
SELECT full_name, email FROM USER_ACCOUNT WHERE role = 'admin'
UNION
SELECT full_name, email FROM USER_ACCOUNT WHERE role = 'occupant';

-- Q24: Exits that are available OR emergency exits (UNION)
SELECT * FROM EXIT_POINT WHERE status = 'available'
UNION
SELECT * FROM EXIT_POINT WHERE is_emergency_exit = 1;

-- Q25: Incidents that are active OR critical (UNION)
SELECT * FROM INCIDENT WHERE status = 'active'
UNION
SELECT * FROM INCIDENT WHERE severity_level = 'critical';

-- Q26: Exits that are BOTH available AND emergency exits (INTERSECT)
SELECT * FROM EXIT_POINT WHERE status = 'available'
INTERSECT
SELECT * FROM EXIT_POINT WHERE is_emergency_exit = 1;

-- Q27: Incidents that are BOTH active AND high severity (INTERSECT)
SELECT * FROM INCIDENT WHERE status = 'active'
INTERSECT
SELECT * FROM INCIDENT WHERE severity_level = 'high';

-- Q28: Admin users that also belong to Grand Mall Mgmt (INTERSECT)
SELECT * FROM USER_ACCOUNT WHERE role = 'admin'
INTERSECT
SELECT * FROM USER_ACCOUNT WHERE company_name = 'Grand Mall Mgmt';

-- Q29: Users never assigned an evacuation route (EXCEPT)
SELECT user_id FROM USER_ACCOUNT
EXCEPT
SELECT user_id FROM EVACUATION_ROUTE;

-- Q30: Exits that are NOT blocked (EXCEPT)
SELECT exit_id FROM EXIT_POINT
EXCEPT
SELECT exit_id FROM EXIT_POINT WHERE status = 'blocked';

-- Q31: Incidents that have not been resolved (EXCEPT)
SELECT incident_id FROM INCIDENT
EXCEPT
SELECT incident_id FROM INCIDENT WHERE status = 'resolved';

-- Q32: Floors with no beacon installed (EXCEPT)
SELECT floor_id FROM FLOOR
EXCEPT
SELECT floor_id FROM BEACON;

-- Q33: Users with no location detection record (EXCEPT)
SELECT user_id FROM USER_ACCOUNT
EXCEPT
SELECT user_id FROM USER_LOCATION;
GO

-- ================================================================