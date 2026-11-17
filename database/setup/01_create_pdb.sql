-- =====================================================================
-- Script   : 01_create_pdb.sql
-- Student  : SHEMA Mfizi Cedrick   (ID 29740)
-- Group    : C
-- Project  : PitchGuard - Football Player Training-Load and Injury
--            Monitoring System
-- Course   : INSY 8311 Database Development with PL/SQL (AUCA)
-- Purpose  : Create the project pluggable database and open it.
-- Run as   : SYS AS SYSDBA, connected to the CDB root (CDB$ROOT).
-- =====================================================================

-- 1. Create the PDB from the seed, with its own admin user (DBA role).
CREATE PLUGGABLE DATABASE c_29740_cedrick_pitchguard_db
  ADMIN USER cedrick_admin IDENTIFIED BY cedrick
  ROLES = (DBA)
  FILE_NAME_CONVERT = (
    'C:\APP\SHEMA\PRODUCT\21C\ORADATA\XE\PDBSEED\',
    'C:\APP\SHEMA\PRODUCT\21C\ORADATA\XE\C_29740_CEDRICK_PITCHGUARD_DB\'
  );

-- 2. Open it read/write.
ALTER PLUGGABLE DATABASE c_29740_cedrick_pitchguard_db OPEN;

-- 3. Save the open state so the PDB reopens automatically when the CDB
--    restarts (otherwise it stays MOUNTED after every restart).
ALTER PLUGGABLE DATABASE c_29740_cedrick_pitchguard_db SAVE STATE;

-- 4. Evidence.
SELECT con_id, name, open_mode FROM v$pdbs ORDER BY con_id;
SELECT con_name, state FROM dba_pdb_saved_states;
SELECT SYSDATE FROM dual;
