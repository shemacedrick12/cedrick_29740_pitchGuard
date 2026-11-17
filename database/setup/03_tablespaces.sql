-- =====================================================================
-- Script   : 03_tablespaces.sql
-- Student  : SHEMA Mfizi Cedrick   (ID 29740)
-- Group    : C
-- Project  : PitchGuard - Football Player Training-Load and Injury
--            Monitoring System
-- Course   : INSY 8311 Database Development with PL/SQL (AUCA)
-- Purpose  : Create the project tablespaces (data, index, temporary)
--            and assign them to the PDB administrator account.
-- Run as   : CEDRICK_ADMIN, connected to c_29740_cedrick_pitchguard_db
-- =====================================================================

-- 1. Data tablespace: 100 MB, grows by 10 MB up to 1 GB.
CREATE TABLESPACE pitchguard_data
  DATAFILE 'C:\APP\SHEMA\PRODUCT\21C\ORADATA\XE\C_29740_CEDRICK_PITCHGUARD_DB\PITCHGUARD_DATA01.DBF'
  SIZE 100M AUTOEXTEND ON NEXT 10M MAXSIZE 1G;

-- 2. Index tablespace: 50 MB, grows by 10 MB up to 500 MB.
CREATE TABLESPACE pitchguard_idx
  DATAFILE 'C:\APP\SHEMA\PRODUCT\21C\ORADATA\XE\C_29740_CEDRICK_PITCHGUARD_DB\PITCHGUARD_IDX01.DBF'
  SIZE 50M AUTOEXTEND ON NEXT 10M MAXSIZE 500M;

-- 3. Temporary tablespace: 50 MB, grows by 10 MB up to 500 MB.
CREATE TEMPORARY TABLESPACE pitchguard_temp
  TEMPFILE 'C:\APP\SHEMA\PRODUCT\21C\ORADATA\XE\C_29740_CEDRICK_PITCHGUARD_DB\PITCHGUARD_TEMP01.DBF'
  SIZE 50M AUTOEXTEND ON NEXT 10M MAXSIZE 500M;

-- 4. Point the admin account at them (instead of SYSTEM / TEMP) and
--    give it unlimited quota on the data and index tablespaces.
ALTER USER cedrick_admin
  DEFAULT TABLESPACE pitchguard_data
  TEMPORARY TABLESPACE pitchguard_temp
  QUOTA UNLIMITED ON pitchguard_data
  QUOTA UNLIMITED ON pitchguard_idx;

-- 5. Evidence: size, autoextend and maximum size.
COL tablespace_name FORMAT A18
SELECT tablespace_name, ROUND(bytes/1024/1024) AS size_mb,
       autoextensible, ROUND(maxbytes/1024/1024) AS max_mb,
       TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS') AS checked_at
FROM   dba_data_files
WHERE  tablespace_name LIKE 'PITCHGUARD%'
UNION ALL
SELECT tablespace_name, ROUND(bytes/1024/1024),
       autoextensible, ROUND(maxbytes/1024/1024),
       TO_CHAR(SYSDATE,'YYYY-MM-DD HH24:MI:SS')
FROM   dba_temp_files
WHERE  tablespace_name LIKE 'PITCHGUARD%'
ORDER  BY 1;

-- 6. Evidence: the account's default / temporary tablespaces.
SELECT username, default_tablespace, temporary_tablespace
FROM   dba_users
WHERE  username = 'CEDRICK_ADMIN';
