# PitchGuard: Football Player Training-Load and Injury Monitoring System

- **Student:** SHEMA Mfizi Cedrick, ID 29740
  
- **Course:** INSY 8311, Database Development with PL/SQL, Adventist University of Central Africa (AUCA)
  
- **Instructor:** Eric Maniraguha
  
- **Phase:** 0, Research, Data Source and Proposal

## Problem statement

Football coaches often notice that a player is overworked only after she is injured. Training load, sleep, soreness and fatigue are recorded in separate files or apps, and nothing enforces simple safety rules, such as keeping an injured player out of training. Injuries are common and costly: in elite women's football, about 6.7 injuries occur per 1000 hours played, and an elite team can expect about 35 time-loss injuries a season (UEFA Women's Elite Club Injury Study, 2024).

## Objectives

**Main objective:** Build an Oracle PL/SQL database that records players' training load, wellness and injuries, and warns coaches when a player is at risk.

**Specific objectives**
- Store players, sessions, training loads, wellness reports and injuries in a normalized (3NF) Oracle database loaded with real data.
- Calculate each player's acute-to-chronic load ratio with a PL/SQL function and flag high-risk players.
- Enforce safety rules with triggers (for example, block an injured player from a training session).
- Keep an audit log of every sensitive action, including blocked attempts.
- Show a live risk dashboard to coaches, connected to the Oracle database.

## Data source

**SoccerMon** (Simula Research Laboratory): training load, daily wellness and injury reports from two Norwegian women's elite teams, 2020 and 2021 seasons. I use the subjective part only (50 players, 33,849 reports, about 9.3 MB). Players appear only as random anonymized IDs, so no real person can be identified.

- Dataset page: https://datasets.simula.no/soccermon/
- Files: https://osf.io/uryz9/
- Licence: CC BY 4.0 (educational use allowed with attribution)

## Innovation

Analytics dashboard (Power BI) connected live to the Oracle database. It shows each player's risk status (red, amber or green), load trends and open injuries. Business rules stay in PL/SQL; the dashboard only shows the data. (Oracle APEX is the fallback tool if Power BI cannot connect.)

## Planned tables (to be refined in Phase II)

| Table | Purpose |
|---|---|
| TEAM | Teams in the dataset |
| PLAYER | Anonymized player ID and team |
| TRAINING_SESSION | A training session or match (date, type, duration) |
| SESSION_LOAD | A player's load for a session (perceived exertion, duration) |
| WELLNESS_REPORT | Daily fatigue, sleep, soreness, stress and mood |
| INJURY | Injury location, severity, start and end date |
| RISK_ALERT | Alerts raised by the risk function |
| AUDIT_LOG | Who tried what and when, including denied actions |

## Planned PL/SQL features

| Feature | Where it is used |
|---|---|
| Procedure `record_session` | Saves a player's load for a session after checking the rules |
| Procedure `report_injury` | Opens an injury and logs it |
| Function `calc_load_ratio(player_id)` | Returns the acute:chronic load ratio |
| Function `get_risk_status(player_id)` | Returns RED, AMBER or GREEN for the dashboard |
| Cursor | Loops through all players, flags high risk and writes alerts |
| Package `pitchguard_pkg` | Groups the procedures and functions |
| Trigger | Blocks an injured player from being added to a session |
| Trigger | Writes every insert, update and denied attempt to the audit log |
| Exception handling | Player not found, invalid load value, duplicate report |

## References

- Bartels, F., Xing, L., Midoglu, C., Boeker, M., Kirsten, T., & Halvorsen, P. (2024). SoccerGuard: Investigating injury risk factors for professional soccer players with machine learning (arXiv:2411.08901). https://arxiv.org/abs/2411.08901
- Oracle. (2019). Oracle Database PL/SQL Language Reference, Release 19. https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/overview-triggers.html
- Rossi, A., Pappalardo, L., Cintia, P., Iaia, F. M., Fernàndez, J., & Medina, D. (2018). Effective injury forecasting in soccer with GPS training data and machine learning. PLOS ONE, 13(7), e0201264. https://doi.org/10.1371/journal.pone.0201264
- Simula Research Laboratory. (n.d.). SoccerMon dataset [Data set]. https://datasets.simula.no/soccermon/
- UEFA Women's Elite Club Injury Study. (2024). British Journal of Sports Medicine, 58(3), 128-135. https://doi.org/10.1136/bjsports-2023-107133

Full list with findings: `docs/research/research_log.md`
