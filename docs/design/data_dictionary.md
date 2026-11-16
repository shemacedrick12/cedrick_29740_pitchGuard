# Data dictionary: PitchGuard logical design

Project: PitchGuard (SHEMA Mfizi Cedrick, ID 29740). This is the logical design in Third Normal Form (see `normalization.md`). The picture is `erd.png`. Oracle data types and sizes are left out on purpose; they are added in Phase IV.

Column keys: PK primary key, FK foreign key, UK unique. "Required" means the column must always have a value (no blanks).

Note on the Phase I diagram: it names a table INJURY. In this design INJURY became three tables (INJURY_REPORT, INJURY_LOCATION and BODY_LOCATION), because one injury report can list several body locations.

## 1. Tables at a glance

| Table | Purpose | Source |
|---|---|---|
| TEAM | The two teams in the dataset | prefix of the player code |
| PLAYER | One anonymised player | 50 player codes |
| SESSION_LOAD | One training session of one player | session.json, 16,265 sessions |
| WELLNESS_REPORT | One player's daily wellness answers | 7 wellness grids, 17,008 player-days |
| INJURY_REPORT | One player's injury report on one day | injury.csv, 156 distinct reports |
| BODY_LOCATION | List of allowed body locations | 11 locations in injury.csv |
| INJURY_LOCATION | Which body locations a report lists, and how severe | injury.csv, 299 location records |
| RISK_ALERT | A warning raised for a player | created by PL/SQL |
| AUDIT_LOG | Record of every action and every refused action | written by triggers |

## 2. Columns

### TEAM

| Column | Key | Required | Unique | Meaning |
|---|---|---|---|---|
| team_id | PK | Yes | Yes | Identifier of the team |
| team_name | | Yes | Yes | Anonymous team label from the dataset: TeamA or TeamB |

### PLAYER

| Column | Key | Required | Unique | Meaning |
|---|---|---|---|---|
| player_id | PK | Yes | Yes | Identifier of the player |
| player_code | | Yes | Yes | Anonymised code from the dataset (team label plus a random identifier). No real name is stored |
| team_id | FK | Yes | No | The team the player belongs to |

### SESSION_LOAD

| Column | Key | Required | Unique | Meaning |
|---|---|---|---|---|
| load_id | PK | Yes | Yes | Identifier of the session record (needed because a player can have two identical sessions on one day) |
| player_id | FK | Yes | No | The player who trained |
| session_date | | Yes | No | Day of the training session |
| rpe | | Yes | No | Rating of perceived exertion, whole number from 0 to 10 |
| duration_min | | Yes | No | Length of the session in minutes (0 to 190 in the data) |
| srpe | calculated | n/a | n/a | Session load, rpe x duration_min. Calculated by the database, not typed in (removed from stored columns to keep 3NF) |

### WELLNESS_REPORT

| Column | Key | Required | Unique | Meaning |
|---|---|---|---|---|
| wellness_id | PK | Yes | Yes | Identifier of the report |
| player_id | FK | Yes | with report_date | The player who answered |
| report_date | | Yes | with player_id | Day of the report. One report per player per day: (player_id, report_date) is unique |
| fatigue | | No | No | Fatigue rating, 1 to 5 |
| mood | | No | No | Mood rating, 1 to 5 |
| readiness | | No | No | Readiness to train rating, 1 to 10 |
| sleep_duration_h | | No | No | Hours slept, 1 to 12, may have decimals |
| sleep_quality | | No | No | Sleep quality rating, 1 to 5 |
| soreness | | No | No | Muscle soreness rating, 1 to 5 |
| stress | | No | No | Stress rating, 1 to 5 |

The seven answers are not required because 77 of the 17,008 reports skip some questions.

### INJURY_REPORT

| Column | Key | Required | Unique | Meaning |
|---|---|---|---|---|
| injury_id | PK | Yes | Yes | Identifier of the injury report |
| player_id | FK | Yes | with report_date | The player who reported pain or injury |
| report_date | | Yes | with player_id | Day of the report. One injury report per player per day |

### BODY_LOCATION

| Column | Key | Required | Unique | Meaning |
|---|---|---|---|---|
| location_id | PK | Yes | Yes | Identifier of the body location |
| location_code | | Yes | Yes | Label from the dataset, for example right_knee. The 11 values are: groin_hip, head_neck, left_foot, left_knee, left_leg, left_thigh, right_foot, right_knee, right_leg, right_thigh, stomach_back |

### INJURY_LOCATION (junction table)

| Column | Key | Required | Unique | Meaning |
|---|---|---|---|---|
| injury_id | PK, FK | Yes | with location_id | The injury report |
| location_id | PK, FK | Yes | with injury_id | The body location in that report |
| severity | | Yes | No | How serious: minor or major |

The primary key is the pair (injury_id, location_id): a location appears once per report.

### RISK_ALERT

| Column | Key | Required | Unique | Meaning |
|---|---|---|---|---|
| alert_id | PK | Yes | Yes | Identifier of the alert |
| player_id | FK | Yes | No | The player the alert is about |
| alert_date | | Yes | No | Day the alert was raised |
| alert_type | | Yes | No | Why: HIGH_LOAD (load ratio too high) or BLOCKED_ENTRY (a load entry for an injured player was refused) |
| risk_status | | Yes | No | RED or AMBER, as decided when the alert was raised (kept as a record, because the limits may change later) |
| load_ratio | | No | No | Acute:chronic load ratio that caused the alert. Empty for BLOCKED_ENTRY |
| alert_status | | Yes | No | OPEN when raised, ACKNOWLEDGED after the coach decides, ARCHIVED at season end |
| coach_decision | | No | No | The coach's decision: REST, REDUCE_LOAD or MONITOR. Empty until the coach decides |
| decided_at | | No | No | Date and time of the coach's decision. Empty until the coach decides |

### AUDIT_LOG

| Column | Key | Required | Unique | Meaning |
|---|---|---|---|---|
| audit_id | PK | Yes | Yes | Identifier of the log entry |
| player_id | FK | No | No | The player concerned, when there is one |
| action_time | | Yes | No | Date and time of the attempt |
| db_user | | Yes | No | Database user who tried the action |
| action | | Yes | No | What was tried: INSERT, UPDATE or DELETE |
| table_name | | Yes | No | Table the action was tried on |
| outcome | | Yes | No | ALLOWED or DENIED |
| details | | No | No | Short text, for example why an entry was refused |

## 3. Relationships

| Parent (one) | Child (many) | Reading | Optionality |
|---|---|---|---|
| TEAM | PLAYER | One team has zero or many players; each player belongs to exactly one team | team_id required in PLAYER |
| PLAYER | SESSION_LOAD | One player has zero or many sessions; each session belongs to exactly one player | player_id required |
| PLAYER | WELLNESS_REPORT | One player has zero or many reports; each report belongs to exactly one player | player_id required |
| PLAYER | INJURY_REPORT | One player has zero or many injury reports; each report belongs to exactly one player | player_id required |
| INJURY_REPORT | INJURY_LOCATION | One report lists one or many locations; each row belongs to exactly one report | a report must list at least one location |
| BODY_LOCATION | INJURY_LOCATION | One location appears in zero or many rows; each row refers to exactly one location | location_id required |
| PLAYER | RISK_ALERT | One player has zero or many alerts; each alert is about exactly one player | player_id required |
| PLAYER | AUDIT_LOG | One player appears in zero or many log entries; a log entry refers to zero or one player | player_id optional |

Many-to-many relationship: an injury report can list many body locations and a body location can appear in many reports. It is resolved by the junction table INJURY_LOCATION.

## 4. Where the Phase I process uses each table

| Step | Table |
|---|---|
| A4 Validate entry | reads PLAYER |
| A5 Reject entry, log denial | writes AUDIT_LOG (outcome DENIED) |
| A6 Check recent major injury | reads INJURY_REPORT and INJURY_LOCATION (severity major) |
| A7 Block entry, raise alert | writes AUDIT_LOG and RISK_ALERT (alert_type BLOCKED_ENTRY) |
| A8 Save entry | writes SESSION_LOAD, WELLNESS_REPORT, INJURY_REPORT, INJURY_LOCATION and AUDIT_LOG |
| A9 Calculate load ratio | reads SESSION_LOAD |
| A10 Create risk alert | writes RISK_ALERT (alert_type HIGH_LOAD) |
| A11 Refresh dashboard | reads RISK_ALERT, PLAYER, SESSION_LOAD |
| A12 Review alerts | reads RISK_ALERT, PLAYER |
| A14 Record decision | updates RISK_ALERT (coach_decision, decided_at, alert_status) |
| A15 Archive resolved alerts | updates RISK_ALERT (alert_status ARCHIVED) |
