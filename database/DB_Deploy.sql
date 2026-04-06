-- ================================================================
--  SMART EVACUATION NAVIGATION SYSTEM
--  SQL Server (T-SQL)  |  Physical Implementation
-- ================================================================

USE SmartEvacuationDB;
GO

-- ================================================================
-- Chapter 10 : DEPLOY & BACKUP DATABASE
-- ================================================================

-- ----------------------------------------------------------------
-- SECTION A: Verify all objects exist
-- ----------------------------------------------------------------

-- List all tables
SELECT TABLE_NAME AS [Table], TABLE_TYPE AS [Type]
FROM   INFORMATION_SCHEMA.TABLES
WHERE  TABLE_TYPE = 'BASE TABLE'
ORDER  BY TABLE_NAME;
GO

-- Row counts for every table
SELECT 'BUILDING'           AS [Table], COUNT(*) AS [Rows] FROM BUILDING
UNION ALL SELECT 'FLOOR',            COUNT(*) FROM FLOOR
UNION ALL SELECT 'ZONE',             COUNT(*) FROM ZONE
UNION ALL SELECT 'BEACON',           COUNT(*) FROM BEACON
UNION ALL SELECT 'EXIT_POINT',       COUNT(*) FROM EXIT_POINT
UNION ALL SELECT 'STAIRCASE',        COUNT(*) FROM STAIRCASE
UNION ALL SELECT 'STAIRCASE_FLOOR',  COUNT(*) FROM STAIRCASE_FLOOR
UNION ALL SELECT 'USER_ACCOUNT',     COUNT(*) FROM USER_ACCOUNT
UNION ALL SELECT 'EMPLOYEE',         COUNT(*) FROM EMPLOYEE
UNION ALL SELECT 'USER_LOCATION',    COUNT(*) FROM USER_LOCATION
UNION ALL SELECT 'INCIDENT',         COUNT(*) FROM INCIDENT
UNION ALL SELECT 'EVACUATION_ROUTE', COUNT(*) FROM EVACUATION_ROUTE
UNION ALL SELECT 'ROUTE_STEP',       COUNT(*) FROM ROUTE_STEP
UNION ALL SELECT 'NODE',             COUNT(*) FROM NODE
UNION ALL SELECT 'EDGE',             COUNT(*) FROM EDGE;
GO

-- List all views
SELECT TABLE_NAME AS [View]
FROM   INFORMATION_SCHEMA.VIEWS
ORDER  BY TABLE_NAME;
GO

-- List all indexes
SELECT
    t.name     AS [Table],
    i.name     AS [Index],
    i.type_desc AS [Type]
FROM sys.indexes i
JOIN sys.tables  t ON i.object_id = t.object_id
WHERE i.name IS NOT NULL
ORDER BY t.name, i.name;
GO

-- List all triggers
SELECT
    t.name                   AS [Trigger],
    OBJECT_NAME(t.parent_id) AS [On Table],
    t.type_desc              AS [Type]
FROM sys.triggers t
ORDER BY t.name;
GO

-- List all stored procedures
SELECT name AS [Stored Procedure], create_date AS [Created]
FROM   sys.procedures
ORDER  BY name;
GO

-- List all database users and their permissions
SELECT
    dp.name           AS [User],
    dp.type_desc      AS [Type],
    ISNULL(o.name,'(schema-level)') AS [Object],
    p.permission_name,
    p.state_desc      AS [State]
FROM sys.database_permissions p
JOIN sys.database_principals  dp ON p.grantee_principal_id = dp.principal_id
LEFT JOIN sys.objects          o  ON p.major_id             = o.object_id
WHERE dp.name NOT IN ('public','dbo','guest','INFORMATION_SCHEMA','sys')
ORDER BY dp.name, o.name;
GO

-- ----------------------------------------------------------------
-- SECTION B: Backup database
-- Update the path below to match your server before running.
-- ----------------------------------------------------------------

-- BACKUP DATABASE SmartEvacuationDB
-- TO DISK = 'C:\Backups\SmartEvacuationDB.bak'
-- WITH FORMAT,
--      NAME = 'SmartEvacuationDB Full Backup',
--      DESCRIPTION = 'Smart Evacuation Navigation System - Full Backup';
-- GO

-- ----------------------------------------------------------------
-- SECTION C: Test stored procedures
-- ----------------------------------------------------------------

-- Get all currently active incidents
EXEC sp_get_active_incidents;
GO

-- Get available emergency exits for floor 2
EXEC sp_get_available_exits @p_floor_id = 2;
GO

-- Get statistics for building 1 (Grand Mall)
EXEC sp_get_building_stats @p_building_id = 1;
GO

-- Get evacuation history for user 2 (Bob Smith)
EXEC sp_get_user_history @p_user_id = 2;
GO

-- ----------------------------------------------------------------
-- SECTION D: Sample view queries
-- ----------------------------------------------------------------

SELECT TOP 5 * FROM vw_active_incidents      ORDER BY severity_level DESC;
GO
SELECT TOP 5 * FROM vw_available_emergency_exits;
GO
SELECT TOP 5 * FROM vw_beacon_summary;
GO
SELECT TOP 5 * FROM vw_employee_directory;
GO
SELECT TOP 5 * FROM vw_evacuation_details    ORDER BY route_id, step_number;
GO
SELECT TOP 5 * FROM vw_location_audit;
GO
SELECT *       FROM vw_incident_summary      ORDER BY total_incidents DESC;
GO