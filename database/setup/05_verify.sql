-- =====================================================================
-- Script   : 05_verify.sql
-- Student  : SHEMA Mfizi Cedrick   (ID 29740)
-- Group    : C
-- Project  : PitchGuard - Football Player Training-Load and Injury
--            Monitoring System
-- Course   : INSY 8311 Database Development with PL/SQL (AUCA)
-- Purpose  : Verify the whole Phase III setup in one run.
-- Run as   : CEDRICK_ADMIN, connected to c_29740_cedrick_pitchguard_db
-- =====================================================================

-- 1. PDB, open mode, archive log mode, connected user, time.
SELECT p.name                                  AS pdb_name,
       p.open_mode,
       d.log_mode,
       SYS_CONTEXT('USERENV','SESSION_USER')   AS connected_user,
       TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS') AS checked_at
FROM   v$pdbs p, v$database d;

-- 2. Project tablespaces: size, autoextend, maximum size.
SELECT tablespace_name, ROUND(bytes/1024/1024) AS size_mb,
       autoextensible, ROUND(maxbytes/1024/1024) AS max_mb
FROM   dba_data_files
WHERE  tablespace_name LIKE 'PITCHGUARD%'
UNION ALL
SELECT tablespace_name, ROUND(bytes/1024/1024),
       autoextensible, ROUND(maxbytes/1024/1024)
FROM   dba_temp_files
WHERE  tablespace_name LIKE 'PITCHGUARD%'
ORDER  BY 1;

-- 3. Admin user: status, default and temporary tablespace.
SELECT username, account_status, default_tablespace, temporary_tablespace
FROM   dba_users
WHERE  username = 'CEDRICK_ADMIN';

-- 4. Quotas (max_bytes = -1 means UNLIMITED) and roles.
SELECT username, tablespace_name, max_bytes
FROM   dba_ts_quotas
WHERE  username = 'CEDRICK_ADMIN'
ORDER  BY tablespace_name;

SELECT grantee, granted_role
FROM   dba_role_privs
WHERE  grantee = 'CEDRICK_ADMIN'
ORDER  BY granted_role;
