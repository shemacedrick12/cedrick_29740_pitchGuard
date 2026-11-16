# Dataset card: SoccerMon (subjective part)

Project: PitchGuard, football player training-load and injury monitoring (SHEMA Mfizi Cedrick, ID 29740, INSY 8311).

## 1. Source

| Item | Value |
|---|---|
| Dataset | SoccerMon: a large-scale multivariate soccer athlete health, performance, and position monitoring dataset |
| Authors | Midoglu, Boeker, Kjæreng Winther, Pettersen, Johansen, Riegler, Halvorsen, Hicks (2022) |
| Link | https://doi.org/10.5281/zenodo.10033832 (files: https://zenodo.org/records/10033832) |
| Dataset page | https://datasets.simula.no/soccermon/ |
| Version, published | v1, 5 September 2022 |
| Licence | Creative Commons Attribution 4.0 (CC BY 4.0): use allowed with attribution |
| File used | `subjective.zip` only (the objective files are 99 GB and are not used) |
| Date collected | 10 November 2026 (downloaded from Zenodo for this project) |
| Period covered | 1 January 2020 to 31 December 2021, two Norwegian women's elite teams (TeamA, TeamB) |

## 2. Format and size

`data/raw/subjective.zip` is the file exactly as downloaded: 705,770 bytes (705.8 kB), MD5 `a3e86aeca611f77c9331a535eae00bf7`, which is the checksum published by Zenodo. `data/raw/subjective/` holds the same 19 files extracted without any change (3.7 MB, checked byte for byte against the zip), so a record can be opened directly. Nothing in `data/raw/` has been edited.

| Folder | Files | Format and layout |
|---|---|---|
| wellness | 7: fatigue, mood, readiness, sleep_duration, sleep_quality, soreness, stress | CSV, wide grid: 731 date rows by 50 player columns |
| training-load | 8 derived grids: acwr, atl, ctl28, ctl42, daily_load, monotony, strain, weekly_load | CSV, wide grid: 731 date rows by 50 player columns |
| training-load | session.json | JSON, nested: one list of session objects per player |
| injury | injury.csv | CSV, 3 columns, the injury column holds JSON text |
| illness | illness.csv | CSV, 3 columns, the problems column holds a JSON list |
| game-performance | game-performance.csv | CSV, 5 columns |

## 3. What one record represents

| File | One record is | Records |
|---|---|---|
| session.json | one training session of one player (RPE, minutes, load) | 16,265 |
| wellness (7 grids) | one non-empty cell: one player's answer to one question on one day | 118,959 cells, 17,008 player-days |
| injury.csv | one injury report row: one player, one date, one or more body locations with severity | 162 rows, 306 location records |
| illness.csv | one illness report row: one player, one date, a list of problems | 15 rows, 32 problems |
| game-performance.csv | one player's self-rated performance in one match | 248 |

The main record for the project is the training session. The dataset is far above the 500-record minimum.

## 4. Anonymisation

Players appear only as codes such as `TeamA-d7299614-fa73-4f69-b5e9-f913e3154ff6` (a team name and a random identifier). There are 50 players (27 TeamA, 23 TeamB). The files contain no names, phone numbers, ID numbers or other personal data.

## 5. Data quality report (counts only, nothing has been fixed)

How each field is used or dropped is in `docs/design/normalization.md`, section 6.

| # | Check | Result | Where | Fix in Phase IV |
|---|---|---|---|---|
| 1 | Wide layout: one column per player | 50 player columns repeated in each of 15 grid files (731 rows x 50 = 36,550 cells per file) | wellness, training-load grids | Unpivot to one row per player and date |
| 2 | Empty cells | 136,891 of 255,850 wellness cells empty (53.5%); 19,551 to 19,569 per file | 7 wellness grids | Drop empty cells, keep only answered ones |
| 3 | Incomplete wellness reports | 77 of 17,008 player-days miss 1 to 6 of the 7 answers (68 miss one answer) | wellness | Allow NULL in the 7 answer columns |
| 4 | Dates stored as text, format dd.mm.yyyy | All dates: 731 per grid file (10,965 in 15 files), 16,265 in session.json, 162 injury, 15 illness, 248 game rows; 0 invalid | all files | Convert with TO_DATE(..., 'DD.MM.YYYY') |
| 5 | First column name differs between files | 7 different names: Date, Fatigue Data, Mood Data, Readiness Data, SleepDurH Data, SleepQuality Data, Soreness Data | 15 grid files | Rename to one name, report_date |
| 6 | Team and player joined in one text value | 50 of 50 player codes carry the team name as a prefix | all files | Split into TEAM and PLAYER |
| 7 | Nested JSON values | injury: 162 rows hold a JSON object, 68 rows (42%) have 2 or more locations (306 location records); illness: 15 rows hold lists (32 problems); session.json: 16,265 objects nested under 50 players | injury.csv, illness.csv, session.json | Parse into child rows |
| 8 | Exact duplicate rows | injury 6 rows (7 after expanding the JSON, 299 unique locations); game-performance 1 row | injury.csv, game-performance.csv | Remove duplicates |
| 9 | Possible duplicate sessions | 76 sessions repeat another session of the same player, day, RPE and minutes; 1,968 player-days have more than one session (up to 6 a day), so some may be genuine | session.json | Review, keep real second sessions |
| 10 | Zero or extreme values | 6 sessions with RPE 0 or 0 minutes; 1 session of 190 minutes (longest other is 180) | session.json | Check, reject or keep |
| 11 | Different scales | readiness 1 to 10; fatigue, mood, sleep quality, soreness, stress 1 to 5; sleep duration 1 to 12 hours | wellness | Document scale, add CHECK ranges |
| 12 | Long decimals | 5,437 of 16,981 sleep durations are not whole hours (for example 7.833333333333333) | sleep_duration.csv | Round to 2 decimals |
| 13 | Derived values stored | 8 grids hold 292,400 values (8 x 36,550) that can be calculated from session.json; load in session.json equals RPE x minutes in all 16,265 sessions (0 exceptions) | training-load | Do not load grids; calculate with functions |
| 14 | Rest days stored as 0 | 22,359 zero cells in daily_load.csv (rest days) against 14,191 days with load | daily_load.csv | Not loaded (no session row means rest) |
| 15 | Misspelled value | "soar throat" appears 10 times in 32 illness entries (should be "sore throat") | illness.csv | Not needed: illness.csv is not loaded in the 3NF design (it stays in data/raw). Correct to "sore throat" if it is ever loaded |
| 16 | Mixed line endings | 3 files use CRLF (injury, illness, game-performance), 16 use LF | 19 files | Handle when loading |
| 17 | Missing fields in sessions | 0 missing; sessions per player range from 8 to 645 | session.json | None |
| 18 | Orphan player references | 0 players in injury, illness or game files are missing from session.json | all files | None |

## 6. Checks done

All counts above were produced by reading the raw files without changing them, and are reproducible with the profiling script in `data/scripts/profile_raw.py`.

## 7. Citation

Midoglu, C., Boeker, M., Kjæreng Winther, A., Pettersen, S. A., Johansen, D., Riegler, M., Halvorsen, P., & Hicks, S. (2022). *SoccerMon: A large-scale multivariate soccer athlete health, performance, and position monitoring dataset* (Version v1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.10033832
