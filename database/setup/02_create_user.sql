-- =====================================================================
-- Script   : 02_create_user.sql
-- Student  : SHEMA Mfizi Cedrick   (ID 29740)
-- Group    : C
-- Project  : PitchGuard - Football Player Training-Load and Injury
--            Monitoring System
-- Course   : INSY 8311 Database Development with PL/SQL (AUCA)
-- Purpose  : Give the PDB administrator account the full DBA role and
--            verify it.
-- Run as   : CEDRICK_ADMIN (or SYS AS SYSDBA); the script switches
--            into the PDB itself.
-- Note     : The account cedrick_admin (password = first name, lab-only
--            convention) was created by the ADMIN USER clause of
--            01_create_pdb.sql. Oracle gave it only PDB_DBA, so the full
--            DBA role is granted here. Its default / temporary
--            tablespaces and quotas are set in 03_tablespaces.sql, once
--            those tablespaces exist.
-- =====================================================================

-- 1. Move this session into the project PDB.
ALTER SESSION SET CONTAINER = c_29740_cedrick_pitchguard_db;
SHOW CON_NAME

-- 2. Grant the DBA role (idempotent: re-running does no harm).
GRANT DBA TO cedrick_admin;

-- 3. Verify: roles granted (DBA and PDB_DBA expected).
SELECT grantee, granted_role,
       TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS') AS checked_at
FROM   dba_role_privs
WHERE  grantee = 'CEDRICK_ADMIN'
ORDER  BY granted_role;

-- 4. Verify: account status and current tablespaces.
SELECT username, account_status, default_tablespace, temporary_tablespace
FROM   dba_users
WHERE  username = 'CEDRICK_ADMIN';
