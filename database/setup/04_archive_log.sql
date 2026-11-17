-- =====================================================================
-- Script   : 04_archive_log.sql
-- Student  : SHEMA Mfizi Cedrick   (ID 29740)
-- Group    : C
-- Project  : PitchGuard - Football Player Training-Load and Injury
--            Monitoring System
-- Course   : INSY 8311 Database Development with PL/SQL (AUCA)
-- Purpose  : Switch the database to ARCHIVELOG mode.
-- Run as   : SYS AS SYSDBA in SQL*Plus, connected to the CDB root.
--
-- WHY (scope: CDB, not PDB):
-- Redo logging and archiving belong to the whole container database:
-- every PDB shares ONE set of online redo logs and archived logs, so
-- ARCHIVELOG cannot be switched on for a single PDB. It needs SYSDBA
-- in CDB$ROOT and a restart (SHUTDOWN, STARTUP MOUNT) that affects all
-- PDBs. ARCHIVELOG keeps every redo log so the data can be recovered
-- to any point in time after a failure, which a monitoring system
-- holding player load and injury history needs.
-- =====================================================================

SET LINESIZE 200
COL name FORMAT A12

-- 1. State BEFORE.
ARCHIVE LOG LIST
SELECT name, log_mode FROM v$database;

-- 2. Restart into MOUNT, enable archiving, open.
SHUTDOWN IMMEDIATE
STARTUP MOUNT
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE OPEN;

-- 3. State AFTER.
ARCHIVE LOG LIST
SELECT name, log_mode,
       TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS') AS checked_at
FROM   v$database;

-- 4. Force an archive and confirm the PDB reopened (SAVE STATE).
ALTER SYSTEM ARCHIVE LOG CURRENT;
SHOW PDBS
