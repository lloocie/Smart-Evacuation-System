-- ================================================================
--  SMART EVACUATION NAVIGATION SYSTEM
--  SQL Server  |  Physical Implementation
-- ================================================================

-- CHAPTER 1 : DATABASE CREATION

USE master;
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = 'SmartEvacuationDB')
BEGIN
    ALTER DATABASE SmartEvacuationDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE SmartEvacuationDB;
END
GO
 
CREATE DATABASE SmartEvacuationDB;
GO
 
 
USE SmartEvacuationDB;
GO
 