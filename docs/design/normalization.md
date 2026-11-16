# Normalization: from raw SoccerMon files to Third Normal Form

Project: PitchGuard (SHEMA Mfizi Cedrick, ID 29740). Source: `data/raw/subjective/` (see `data/dataset_card.md`). Every row shown below is a real row from the raw files; player codes are shortened to their first 14 characters followed by `…` so the tables fit the page.

## 1. Entities found

The raw data holds five kinds of records. Three of them are the core of the PitchGuard process (Phase I) and are normalised below.

| Raw source | What the raw data looks like | Rule applied | Entities that come out |
|---|---|---|---|
| 7 wellness grids | one row per date, 50 player columns (a repeating group) | repeating group becomes rows | WELLNESS_REPORT, PLAYER, TEAM |
| session.json | nested: one list of session objects per player | nested list becomes a child table | SESSION_LOAD (child of PLAYER) |
| injury.csv | one JSON object per row, holding several body locations | nested object becomes a child table; many-to-many gets a junction table | INJURY_REPORT, INJURY_LOCATION (junction), BODY_LOCATION |
| 8 derived load grids | values calculated from session.json | derived data is not stored | none (dropped, see section 6) |
| illness.csv, game-performance.csv | extra self-reports not used by the Phase I process | out of scope | none (dropped, see section 6) |

Two more tables are created by the system itself and have no raw data: RISK_ALERT and AUDIT_LOG (the Phase I process creates alerts in A7 and A10, updates them in A14, and logs denials in A5 and A7).

Result: 9 related tables. TEAM, PLAYER, SESSION_LOAD, WELLNESS_REPORT, INJURY_REPORT, BODY_LOCATION, INJURY_LOCATION, RISK_ALERT and AUDIT_LOG.

## 2. Wellness (7 wide grids)

### UNF (unnormalised)

Each of the 7 files (fatigue, mood, readiness, sleep_duration, sleep_quality, soreness, stress) is a grid: one row per date and one column per player. This is `fatigue.csv`, 3 of its 50 player columns:

| Fatigue Data | TeamA-d7299614… | TeamA-b58af410… | TeamA-5cd7a61b… | … 47 more player columns |
|---|---|---|---|---|
| 20.03.2020 | 3 | 3 | 3 | … |
| 21.03.2020 | 3 | 3 | 3 | … |
| 22.03.2020 | 3 | 2 | 3 | … |

Problem: the player columns are a **repeating group** (50 columns of the same kind), and the 7 questions are spread over 7 files. A new player would need a new column.

### 1NF

Remove the repeating group: one row per player per date, all 7 answers side by side, every cell holds a single value. Empty cells (53.5% of the grid) produce no row. Key: (report_date, player_code).

| report_date | player_code | fatigue | mood | readiness | sleep_duration_h | sleep_quality | soreness | stress |
|---|---|---|---|---|---|---|---|---|
| 20.03.2020 | TeamA-d7299614… | 3 | 3 | 7 | 9.0 | 3 | 2 | 3 |
| 20.03.2020 | TeamA-b58af410… | 3 | 2 | 6 | 9.0 | 3 | 2 | 3 |
| 20.03.2020 | TeamA-5cd7a61b… | 3 | 4 | 6 | 8.5 | 3 | 2 | 4 |
| 21.03.2020 | TeamA-d7299614… | 3 | 3 | 7 | 9.0 | 3 | 3 | 3 |
| 21.03.2020 | TeamA-b58af410… | 3 | 3 | 6 | 10.0 | 4 | 2 | 3 |

Dependency removed: **repeating group** (50 player columns become rows, 7 files merge into one table).

### 2NF

The key is composite (report_date, player_code). The 7 answers depend on both parts, but the team name (the prefix of the code, `TeamA` or `TeamB`) depends on player_code alone. That is a **partial dependency**, so players move to their own table.

WELLNESS_REPORT (report_date, player_code, the 7 answers), as above, and

PLAYER:

| player_code | team_name |
|---|---|
| TeamA-d7299614… | TeamA |
| TeamA-b58af410… | TeamA |
| TeamA-5cd7a61b… | TeamA |

Dependency removed: **partial dependency** (team depends only on player_code).

### 3NF

Two changes. First, the long text codes (42 characters) are replaced by short surrogate keys `player_id` and `wellness_id`. Second, PLAYER now holds a team that has its own identity: player_id determines team_id, and team_id determines team_name. That is a **transitive dependency** (player_id, team_id, team_name), so the team moves to TEAM.

TEAM:

| team_id | team_name |
|---|---|
| 1 | TeamA |
| 2 | TeamB |

PLAYER:

| player_id | player_code | team_id |
|---|---|---|
| 1 | TeamA-d7299614… | 1 |
| 2 | TeamA-b58af410… | 1 |
| 3 | TeamA-5cd7a61b… | 1 |

WELLNESS_REPORT:

| wellness_id | player_id | report_date | fatigue | mood | readiness | sleep_duration_h | sleep_quality | soreness | stress |
|---|---|---|---|---|---|---|---|---|---|
| (auto) | 1 | 2020-03-20 | 3 | 3 | 7 | 9.0 | 3 | 2 | 3 |
| (auto) | 2 | 2020-03-20 | 3 | 2 | 6 | 9.0 | 3 | 2 | 3 |
| (auto) | 3 | 2020-03-20 | 3 | 4 | 6 | 8.5 | 3 | 2 | 4 |
| (auto) | 1 | 2020-03-21 | 3 | 3 | 7 | 9.0 | 3 | 3 | 3 |
| (auto) | 2 | 2020-03-21 | 3 | 3 | 6 | 10.0 | 4 | 2 | 3 |

Dependency removed: **transitive dependency** (player_id, then team_id, then team_name). Uniqueness: one report per player per day, (player_id, report_date) is unique.

## 3. Training sessions (session.json)

### UNF

The file is nested JSON: one key per player, holding a **list** of session objects (16,265 sessions for 50 players). Player 1 on 17 March 2020 trained four times:

```json
{
  "TeamA-d7299614…": [
    {"srpe": 300, "rpe": 5, "duration": 60, "date": "17.03.2020"},
    {"srpe": 120, "rpe": 3, "duration": 40, "date": "17.03.2020"},
    {"srpe": 360, "rpe": 6, "duration": 60, "date": "17.03.2020"},
    {"srpe": 120, "rpe": 3, "duration": 40, "date": "17.03.2020"},
    …
  ]
}
```

### 1NF

Flatten the list: one row per session, single values only. The first four rows show why a key is needed: the second and fourth session of that day are identical (RPE 3, 40 minutes), so no combination of player, date, RPE and minutes is unique. A surrogate key `load_id` becomes the key.

| load_id | player_code | date | rpe | duration | srpe |
|---|---|---|---|---|---|
| 1 | TeamA-d7299614… | 17.03.2020 | 5 | 60 | 300 |
| 2 | TeamA-d7299614… | 17.03.2020 | 3 | 40 | 120 |
| 3 | TeamA-d7299614… | 17.03.2020 | 6 | 60 | 360 |
| 4 | TeamA-d7299614… | 17.03.2020 | 3 | 40 | 120 |
| 5 | TeamA-d7299614… | 18.03.2020 | 4 | 60 | 240 |

Dependency removed: **repeating group** (the list of sessions inside each player).

### 2NF

The key is a single column (load_id), so no attribute can depend on only part of it. The table is already in 2NF. No split.

### 3NF

Two **transitive dependencies** are removed:

1. `srpe` equals `rpe` x `duration`. In all 16,265 sessions the stored value matches the calculation (0 exceptions), so it is a calculated value that depends on two other non-key columns. It is not stored as an ordinary column; it becomes a calculated (virtual) column in Phase IV.
2. The player code repeats on every session and has the team hidden inside it: load_id determines the player, and the player determines the team. Player and team facts already live in PLAYER and TEAM (section 2), so SESSION_LOAD keeps only the `player_id` foreign key.

SESSION_LOAD after 3NF:

| load_id | player_id | session_date | rpe | duration_min |
|---|---|---|---|---|
| 1 | 1 | 2020-03-17 | 5 | 60 |
| 2 | 1 | 2020-03-17 | 3 | 40 |
| 3 | 1 | 2020-03-17 | 6 | 60 |
| 4 | 1 | 2020-03-17 | 3 | 40 |
| 5 | 1 | 2020-03-18 | 4 | 60 |

Check, the removed column (real values, for comparison):

| load_id | player_id | session_date | rpe | duration_min | srpe |
|---|---|---|---|---|---|
| 1 | 1 | 2020-03-17 | 5 | 60 | 300 |
| 2 | 1 | 2020-03-17 | 3 | 40 | 120 |
| 3 | 1 | 2020-03-17 | 6 | 60 | 360 |
| 4 | 1 | 2020-03-17 | 3 | 40 | 120 |
| 5 | 1 | 2020-03-18 | 4 | 60 | 240 |

## 4. Injuries (injury.csv)

### UNF

One row per injury report. The `type` column holds a JSON object with one or more body locations (a nested object). Rows 53, 54 and 55 contain two locations each (68 of the 162 rows do):

| csv_row | player_name | type | timestamp |
|---|---|---|---|
| 1 | TeamA-b58af410… | {"right_thigh":"minor"} | 20.03.2020 |
| 2 | TeamA-5cd7a61b… | {"right_foot":"minor"} | 20.03.2020 |
| 53 | TeamA-bcc03f81… | {"right_foot":"minor","right_knee":"minor"} | 20.03.2020 |
| 54 | TeamA-bcc03f81… | {"right_foot":"minor","right_knee":"major"} | 21.03.2020 |
| 55 | TeamA-bcc03f81… | {"right_foot":"minor","right_knee":"major"} | 22.03.2020 |

### 1NF

Remove the repeating group inside `type`: one row per report per body location, single values only. The key is (csv_row, body_location), where csv_row is the number of the report row in injury.csv (it becomes `injury_id`).

| csv_row | player_code | report_date | body_location | severity |
|---|---|---|---|---|
| 1 | TeamA-b58af410… | 20.03.2020 | right_thigh | minor |
| 2 | TeamA-5cd7a61b… | 20.03.2020 | right_foot | minor |
| 53 | TeamA-bcc03f81… | 20.03.2020 | right_foot | minor |
| 53 | TeamA-bcc03f81… | 20.03.2020 | right_knee | minor |
| 54 | TeamA-bcc03f81… | 21.03.2020 | right_foot | minor |
| 54 | TeamA-bcc03f81… | 21.03.2020 | right_knee | major |
| 55 | TeamA-bcc03f81… | 22.03.2020 | right_foot | minor |
| 55 | TeamA-bcc03f81… | 22.03.2020 | right_knee | major |

Dependency removed: **repeating group** (several locations inside one cell). A value like `right_knee` is kept as one atomic location value.

### 2NF

With the composite key (csv_row, body_location), player_code and report_date depend on csv_row alone: row 53 repeats the same player and date for each of its two locations. That is a **partial dependency**, so the report moves to its own table. csv_row is renamed `injury_id`.

INJURY_REPORT:

| injury_id | player_code | report_date |
|---|---|---|
| 1 | TeamA-b58af410… | 20.03.2020 |
| 2 | TeamA-5cd7a61b… | 20.03.2020 |
| 53 | TeamA-bcc03f81… | 20.03.2020 |
| 54 | TeamA-bcc03f81… | 21.03.2020 |
| 55 | TeamA-bcc03f81… | 22.03.2020 |

INJURY_LOCATION:

| injury_id | body_location | severity |
|---|---|---|
| 1 | right_thigh | minor |
| 2 | right_foot | minor |
| 53 | right_foot | minor |
| 53 | right_knee | minor |
| 54 | right_foot | minor |
| 54 | right_knee | major |
| 55 | right_foot | minor |
| 55 | right_knee | major |

Dependency removed: **partial dependency** (player and date depend only on the report).

### 3NF

Three changes:

1. player_code carries the team, the same **transitive dependency** as in section 2, so the report keeps only `player_id`.
2. The location text is repeated 306 times for 11 different values. It is moved to a lookup table, BODY_LOCATION, so only listed values can be used (a misspelling such as the "soar throat" found in illness.csv cannot enter). This is a design choice for controlled values, not a normal-form rule.
3. A report can have many locations and a location appears in many reports: a **many-to-many relationship**. INJURY_LOCATION is the **junction table** between INJURY_REPORT and BODY_LOCATION and holds the severity, which depends on both (the same knee can be minor in one report and major in the next). Its key is (injury_id, location_id).

BODY_LOCATION (11 rows, ids assigned alphabetically):

| location_id | location_code |
|---|---|
| 1 | groin_hip |
| 2 | head_neck |
| 3 | left_foot |
| 4 | left_knee |
| 5 | left_leg |
| 6 | left_thigh |
| 7 | right_foot |
| 8 | right_knee |
| 9 | right_leg |
| 10 | right_thigh |
| 11 | stomach_back |

INJURY_LOCATION:

| injury_id | location_id | severity |
|---|---|---|
| 1 | 10 | minor |
| 2 | 7 | minor |
| 53 | 7 | minor |
| 53 | 8 | minor |
| 54 | 7 | minor |
| 54 | 8 | major |
| 55 | 7 | minor |
| 55 | 8 | major |

INJURY_REPORT now has (injury_id, player_id, report_date), with (player_id, report_date) unique: in the 156 distinct reports no player has two reports on the same day. Severity has only two values (minor, major) and is kept as a column with a check rule, not a table.

## 5. Final 3NF design

| Table | Primary key | Foreign keys | Source |
|---|---|---|---|
| TEAM | team_id | none | prefix of the player code |
| PLAYER | player_id | team_id (TEAM) | the 50 player codes |
| SESSION_LOAD | load_id | player_id (PLAYER) | session.json, 16,265 sessions |
| WELLNESS_REPORT | wellness_id | player_id (PLAYER) | 7 wellness grids, 17,008 player-days |
| INJURY_REPORT | injury_id | player_id (PLAYER) | injury.csv, 156 distinct reports |
| BODY_LOCATION | location_id | none | 11 locations in injury.csv |
| INJURY_LOCATION | (injury_id, location_id) | injury_id, location_id | injury.csv, 299 location records |
| RISK_ALERT | alert_id | player_id (PLAYER) | created by PL/SQL |
| AUDIT_LOG | audit_id | player_id (PLAYER), optional | written by triggers |

Every non-key column depends on the key, the whole key and nothing but the key.

## 6. Field mapping: every raw field to its target

| Raw file | Raw field | Target table.column | Conversion or reason dropped |
|---|---|---|---|
| wellness/*.csv (7 files) | first column (Date, Fatigue Data, Mood Data, ...) | WELLNESS_REPORT.report_date | text dd.mm.yyyy to DATE with TO_DATE(..., 'DD.MM.YYYY') |
| wellness/*.csv | 50 player column headers | PLAYER.player_code and WELLNESS_REPORT.player_id | headers become rows (unpivot); look up player_id |
| wellness/*.csv | team prefix of the header | TEAM.team_name | split at the first `-` |
| fatigue.csv | cell value | WELLNESS_REPORT.fatigue | decimal text (3.0) to whole number; empty cell means no row |
| mood.csv | cell value | WELLNESS_REPORT.mood | as above |
| readiness.csv | cell value | WELLNESS_REPORT.readiness | as above; scale is 1 to 10 |
| sleep_duration.csv | cell value | WELLNESS_REPORT.sleep_duration_h | text to NUMBER, round to 2 decimals (5,437 values are not whole hours) |
| sleep_quality.csv | cell value | WELLNESS_REPORT.sleep_quality | decimal text to whole number |
| soreness.csv | cell value | WELLNESS_REPORT.soreness | as above |
| stress.csv | cell value | WELLNESS_REPORT.stress | as above |
| training-load/session.json | player key | PLAYER.player_code, SESSION_LOAD.player_id | split team prefix; look up player_id |
| session.json | date | SESSION_LOAD.session_date | text dd.mm.yyyy to DATE |
| session.json | rpe | SESSION_LOAD.rpe | whole number 0 to 10 |
| session.json | duration | SESSION_LOAD.duration_min | whole number of minutes |
| session.json | srpe | dropped | derived: equals rpe x duration in all 16,265 sessions; calculated column instead |
| training-load/acwr, atl, ctl28, ctl42, daily_load, monotony, strain, weekly_load (8 files) | all cells (292,400 values) | dropped | derived from session.json; recalculated by PL/SQL; acwr.csv is kept only to check the calculation |
| injury/injury.csv | player_name | INJURY_REPORT.player_id | look up player_id |
| injury.csv | timestamp | INJURY_REPORT.report_date | text dd.mm.yyyy to DATE |
| injury.csv | type (JSON key, e.g. right_knee) | BODY_LOCATION.location_code, INJURY_LOCATION.location_id | parse JSON; one row per key; look up location_id |
| injury.csv | type (JSON value, minor or major) | INJURY_LOCATION.severity | parse JSON |
| illness/illness.csv | player_name, problems, timestamp | dropped | not used by any step of the Phase I process; 15 rows for 4 players; keeping it would add 3 more tables (report, problem list, junction); stays in data/raw |
| game-performance/game-performance.csv | player_name, team_performance, offensive_performance, defensive_performance, timestamp | dropped | match self-ratings are not used by the process (248 rows); stays in data/raw |
| none (system-generated) | n/a | RISK_ALERT.*, AUDIT_LOG.* | created by procedures and triggers, no raw data |

### Cleaning checklist for Phase IV

1. Dates: convert every text date with TO_DATE(..., 'DD.MM.YYYY').
2. Unpivot the 7 wellness grids and merge them on (player, date); skip empty cells.
3. Split the player code into team name and player code; create TEAM and PLAYER first.
4. Parse injury JSON into location and severity; remove the 6 duplicate rows (7 duplicate location records).
5. Convert decimal text such as 3.0 to whole numbers; round sleep duration to 2 decimals.
6. Review the 6 zero-load sessions, the 190-minute session and the 76 repeated sessions.
7. Do not load the 8 derived grids; calculate the load ratio with a function.

## 7. In class: following one record

A session object from session.json (player 1, 17 March 2020):

`{"srpe": 300, "rpe": 5, "duration": 60, "date": "17.03.2020"}`

- The key `TeamA-d7299614…` becomes PLAYER.player_code (player_id 1) and the prefix `TeamA` becomes TEAM.team_name (team_id 1).
- `date` becomes SESSION_LOAD.session_date = 2020-03-17.
- `rpe` becomes SESSION_LOAD.rpe = 5, `duration` becomes SESSION_LOAD.duration_min = 60.
- `srpe` (300) is not stored; the database calculates 5 x 60 = 300.

An injury row from injury.csv (row 53):

`TeamA-bcc03f81-2733-45d3-abf1-f7a709c63e68, {"right_foot":"minor","right_knee":"minor"}, 20.03.2020`

- The player code becomes INJURY_REPORT.player_id, the date becomes INJURY_REPORT.report_date = 2020-03-20.
- `right_foot` and `right_knee` become two INJURY_LOCATION rows (location_id 7 and 8), each with severity `minor`.
