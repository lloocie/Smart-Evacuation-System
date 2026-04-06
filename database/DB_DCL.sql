-- ================================================================
--  SMART EVACUATION NAVIGATION SYSTEM
--  SQL Server (T-SQL)  |  Physical Implementation
--  Compatible with: SQL Server Management Studio (SSMS)
-- ================================================================

USE SmartEvacuationDB;
GO

-- CHAPTER 9 : DCL - ACCESS CONTROL
-- ================================================================

-- Create logins and users for the three access levels
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'evac_admin')
    CREATE LOGIN evac_admin WITH PASSWORD = 'AdminPass2024!';

IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'evac_occupant')
    CREATE LOGIN evac_occupant WITH PASSWORD = 'OccupantPass2024!';

IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'evac_readonly')
    CREATE LOGIN evac_readonly WITH PASSWORD = 'ReadPass2024!';
GO

CREATE USER evac_admin    FOR LOGIN evac_admin;
CREATE USER evac_occupant FOR LOGIN evac_occupant;
CREATE USER evac_readonly FOR LOGIN evac_readonly;
GO

-- evac_admin: Full access
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO evac_admin;
GRANT EXECUTE ON SCHEMA::dbo TO evac_admin;
GO

-- evac_occupant: Read layout data, insert own location
GRANT SELECT ON dbo.BUILDING         TO evac_occupant;
GRANT SELECT ON dbo.FLOOR            TO evac_occupant;
GRANT SELECT ON dbo.ZONE             TO evac_occupant;
GRANT SELECT ON dbo.BEACON           TO evac_occupant;
GRANT SELECT ON dbo.EXIT_POINT       TO evac_occupant;
GRANT SELECT ON dbo.INCIDENT         TO evac_occupant;
GRANT SELECT ON dbo.EVACUATION_ROUTE TO evac_occupant;
GRANT SELECT ON dbo.ROUTE_STEP       TO evac_occupant;
GRANT SELECT, INSERT ON dbo.USER_LOCATION TO evac_occupant;
GRANT EXECUTE ON SCHEMA::dbo TO evac_occupant;
GO

-- evac_readonly: SELECT only
GRANT SELECT ON SCHEMA::dbo TO evac_readonly;
GO