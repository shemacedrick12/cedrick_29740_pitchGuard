# PitchGuard: Football Player Training-Load and Injury Monitoring System

**Student:** SHEMA Mfizi Cedrick, ID 29740
**Course:** INSY 8311, Database Development with PL/SQL, Adventist University of Central Africa (AUCA)
**Instructor:** Eric Maniraguha
**Phase:** 0 (Research, Data Source and Proposal) and I (Business Process Modeling)

## Problem statement

Football coaches often notice that a player is overworked only after she is injured. Training load, sleep, soreness and fatigue are recorded in separate files or apps, and nothing enforces simple safety rules, such as keeping an injured player out of training. Injuries are common and costly: in elite women's football, about 6.7 injuries occur per 1000 hours played, and an elite team can expect about 35 time-loss injuries a season (Hallén et al., 2024).

## Objectives

**Main objective:** Build an Oracle PL/SQL database that records players' training load, wellness and injuries, and warns coaches when a player is at risk.

**Specific objectives**
1. Store players, sessions, training loads, wellness reports and injuries in a normalized (3NF) Oracle database loaded with real data.
2. Calculate each player's acute-to-chronic load ratio with a PL/SQL function and flag high-risk players.
3. Enforce safety rules with triggers (for example, block an injured player from a training session).
4. Keep an audit log of every sensitive action, including blocked attempts.
5. Show a live risk dashboard to coaches, connected to the Oracle database.

## Data source

**SoccerMon** (Midoglu et al., 2022): training load, daily wellness and injury reports from two Norwegian women's elite teams, 2020 and 2021 seasons. I use the subjective part only (50 players, 33,849 reports, about 9.3 MB). Players appear only as random anonymized IDs, so no real person can be identified.

- Dataset page: https://datasets.simula.no/soccermon/
- Files: https://zenodo.org/records/10033832
- Licence: CC BY 4.0 (educational use allowed with attribution)

## Innovation

**Analytics dashboard (Power BI)** connected live to the Oracle database. It shows each player's risk status (red, amber or green), load trends and open injuries. Business rules stay in PL/SQL; the dashboard only shows the data. (Oracle APEX is the fallback tool if Power BI cannot connect.)

## Planned tables (to be refined in Phase II)

| Table | Purpose |
|---|---|
| TEAM | Teams in the dataset |
| PLAYER | Anonymized player ID and team |
| SESSION_LOAD | One player's training session: perceived exertion (RPE), minutes and load (sRPE) |
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
| Trigger | Blocks a new load entry for a player with a recent major injury |
| Trigger | Writes every insert, update and denied attempt to the audit log |
| Exception handling | Player not found, invalid load value, duplicate report |

## References

- Bartels, F., Xing, L., Midoglu, C., Boeker, M., Kirsten, T., & Halvorsen, P. (2024). *SoccerGuard: Investigating injury risk factors for professional soccer players with machine learning* (arXiv:2411.08901). https://arxiv.org/abs/2411.08901
- Hallén, A., Tomás, R., Ekstrand, J., Bengtsson, H., Van den Steen, E., Hägglund, M., & Waldén, M. (2024). UEFA Women's Elite Club Injury Study: A prospective study on 1527 injuries over four consecutive seasons 2018/2019 to 2021/2022 reveals thigh muscle injuries to be most common and ACL injuries most burdensome. *British Journal of Sports Medicine, 58*(3), 128-135. https://doi.org/10.1136/bjsports-2023-107133
- Midoglu, C., Boeker, M., Kjæreng Winther, A., Pettersen, S. A., Johansen, D., Riegler, M., Halvorsen, P., & Hicks, S. (2022). *SoccerMon: A large-scale multivariate soccer athlete health, performance, and position monitoring dataset* (Version v1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.10033832
- Oracle. (2019). *Oracle Database PL/SQL Language Reference, Release 19*. https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/overview-triggers.html
- Rossi, A., Pappalardo, L., Cintia, P., Iaia, F. M., Fernàndez, J., & Medina, D. (2018). Effective injury forecasting in soccer with GPS training data and machine learning. *PLOS ONE, 13*(7), e0201264. https://doi.org/10.1371/journal.pone.0201264

Full list with findings: [docs/research/research_log.md](docs/research/research_log.md)

## Phase I – Business Process Modeling

**Selected business process:** Daily Training Load Recording and Injury-Risk Alert. Players report session effort, wellness and injuries; PitchGuard validates each entry, calculates the acute:chronic load ratio, and alerts the coach with a RED, AMBER or GREEN status so training can be adjusted before an injury happens.

**Modeling tool:** draw.io (diagrams.net), BPMN swimlane diagram

**Published diagram link:** [Open the BPMN diagram in draw.io](https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=business_process.drawio&dark=0#R%3Cmxfile%3E%3Cdiagram%20name%3D%22Business%20Process%22%20id%3D%22pitchguard-bp%22%3E7V3rl5o8Hv5rPKf7oT1cFPGjOtadXTud1Xbfdz71RIiYFokLOKPvX79JIMjVshhAZ5n2HCFAgDzP75oLPXW6O85dsN9%2BwSa0e4pkHnvqQ09RVH0kkR9acgpKlIGiByWWi8ygTD4XrNBfMCwML7QOyIRe4kQfY9tH%2B2ShgR0HGn6iDLgufkuetsF28q57YMFMwcoAdrb0D2T62%2FA1NEk6H%2Fg7RNaW33rIj%2BwAPzss8LbAxG%2BxInXWU6cuxn6wtTtOoU2bjzdMcN3ngqPRk7nQ8ctc4COfvFXmorAezz%2Fxd%2FbhkRybbP2dTQpksglsZDlk24YbeuQVuj4ibTQOi3fINOnFkw12%2FBBD8jDhflgxrSe41SuwD%2BGteopm%2B%2BGJiYfQ%2FnPA%2FMBHj1U5Jico%2Bv7I6uHHyZZFf5%2BRb2znB%2BCawYkPANkn8vvNBchBjkU2FxiY5GcJDeyaQRFwaMmj8%2FPgnj4ukfeL7I1t8nbk98Pk%2BcsTfaY3tLOBAymLEbBcsPsbf2rS1sGDB88Qvh25HB5jbRuiMYd4B32XPtQ2Rph%2ByI63M7tknXMolJqPw3AfhGy2orrOeJONEPJ8%2BBc5hMliH70twR%2B76C%2FyeoCygKL5tkU%2BXO2BQc99IwKfJInnA5ej32foI9ueYhu7rGp1o9N%2F7EQX%2F4KxIxr7y%2BFLjE9yXwh%2F1CL%2B2OAEXZHARnIfQ5agLQJJpUPyApJnTUCE%2BKsLDKr1pOcFadbVvxZChXegXcL4lCLCVZirHeaSXKj98RsVXmnySLU08LZrHOJPTBl0HUCb0jt5PhSrvBUpD385if9QF4F%2Fv8O%2FWOanGBhbkcCqecCqoySwIxHArkqZ5T1Gjs%2FuMpiQ%2F9InuT%2FoKdPotzcgZ03ZkWA%2FWaYP8s%2BWWWm6Bn52%2BJuqW06V8SfJnJ2sm%2Fwn3NmCPX2j3dGi8cKn9X7nfIKv7MXjZOQO5gKsof2MPeQjTB3NNfZ9vCMn2PTABBi%2FLBcfHDPOU%2FaX46T6eB%2FzZA1yT6Iy1MkeuoiARrcfCDIkroDP56IJPvg2cgjdeXhBRQN4%2B2Bng47QPJ9FSogYOSbzQifeabfG9I0s6ECXymFapswB1M1%2Bnkzpylo9y1QoQ0I8aFkpkKGYp%2BxBz6MNrkjQMb2avV1eFFaip2RMgIiNS4kYIxJFkzHwN9oSuAZHRclBKa07OSczOAd%2F0REeYspEbkRgXaQveUXr3Fqy59MWjEiwPtcirQ7rHfKTlNlscBBALZ9nVBWQUBg5Bx96Qk2vnhM3aUkqycOUIRbBpVK%2Bd8elC1xSfsclM4zd30jTO4RXDdNGrYE283IqaIt364P3e8pkOJL2vDKcUQwjjzOmttYGWgFniqxwYEnT9jWyzfVR7ZlYKHIcU1cfsaRNj6YDTUCQ%2BiySJTlhXYokgxRJRLiC41IxXqdbLugWtUC3LOE%2BMEoRbT7Y2ACM0MxEecQLdZF%2FatpGaaMabFSpWLFGHpkA6ptcfaMZOlxvbp9H%2FQIe%2FZvEDybwIXONGSxhxW76VqjkrZYEXUTIF7zB82L8MlvGbo7S9TbEy1EqiaWKUHDzcs5TZwUvkplxsHGDJ8tKihFCQjOtU1VXqiqtQFVNt9Cg%2FVkupLkOGoWBnwnPSazmenz6x%2Fflyw1oLjnKKAhVXeV8s051XST3soCLjSuz%2FqAOZaa3rcx%2Bn0%2B8cWWmF%2BUGwKtAn2vqQurDsWdfzVarx69PPxZfxw9BKPDHbLF4IqU%2FlrPnr8tvQSFXb3R7%2FP3h8Ru5YF63tpPlEuouHYmq2kAAlUdtU%2Fnu7fKoyC4D2zjYQQwBjAPjobF1sYMMUmIHg1RcGpqKNtFJqrdvqIejOgx1ueC3M9SXDXUwFsrzgU9bqWHzTB6sDvPMK%2B3sc2WlRpswX6sFJpVoroA5IBhFJ9JSLx9X%2F%2FwxXsyoSW5deWU6l4Qor%2FGgY%2BiVDB0UEHQJf9I%2B%2B8iHnDJjS3u7TeggOkBIJFcbcxHL2FkpRdWBCKrOunEr72ncCnQSQ1ZIJTvkMDpnB4IZMN%2FFWesDGlfXMWilOKFApRqGg75d6IV9yE2OWJGVlB%2BriRjkOx52puBKUzAsMAUTG7PMaMwSuAB5sB63JWYKprfmxcjpscpCTMOqVDdPZxruxDTkDWn0SW1uJZ3RnG1YQeDxQYzNWgS9Dnsgtx0bQJn%2BywM3GgF%2B4wZBLgoOxq6xRSzDTFwIbL9Ck9sC73pjwCu%2FwSC2Du0%2FK9VT1mn%2FO9H%2BdxoYjEPhlUAgfQ1bgL5SiwloeyD7%2FffKyEUj2ZdwQ3T%2FthefPxYGlWbguYPdmk4yo5uWCyH1LGzkCYgWkr00cQtB78WHhNHtJntwSnU%2BpuMHXRHR%2BSiXCiA6nl%2FiuVLI81cE32LuTTgJfh9OgOZ9Pg2xunUfKENhWRLR2TQv563fVjeknfJO3KAlC72XaN2HsutD1GzvqUYmjLObH0%2BkpcYTEeUpxOCroGVNeP9TAlgb5qvC2UOUN%2FbjKpANTSN2%2F2DQkDAYktHu0AhZErGIAGmLdcenq%2Fm0LsoifJkQk8Zu9wvCPfnxozm1bBokdpBPudUyl6IzruNS27NMNhuoFRi54WgtSXdApaJpJsEaRTQWgQbyoklKwPjl4DcbmpbAvorve%2FNGh1ikRwGJ8cxmXe9El59qPT8VrlgSE3A6UYMIfdOZKrrWSco8yAKkbBOKFNNVcRnLEzt8cI3wrFVWFGkVPNbBrr%2FFFnaAPTuXTs5GRkrSmpBjTBcBpExmnb6s6DOyi%2BKqEjSHR%2BT%2Fyesn2y%2F0tsyy0L2HY%2FgUbOfEd2hP85%2FxndhVdPd8Gdvj1wVt4QPXgj43uzmczGOBC23gs26HWEtfhahSDdFxh%2BhlRJXWEFUrIqp0iF5CdN6ejParITrvZPSyjKoZRF%2Bg1xSog4piqr5vUM84viRgLA1qvz73LloOiYZt53Vs6F60AgUJu8AFX%2B8KZrFLCVrgFDshjGjONT%2FTgrMjONIzKcwUS4Maz5yNHq0cjbX3rpvO1H2Jkbp23ZSl8RNug0BaqiOlrwgm0LCiHuzfC4Faclfac0D1iiqhc0AvqwStTXdl9N5Brabnr3ZXBuL1fPlsjlRR9w7uBdR2JHXWXqjIB5P9z5BqHaQXzWk2VmwM0oopuvk7jxSvtqd6m6q3YpbufkBtyZ4O23SS5IqZOk7F20e1JVEdtad9q%2BbpRh2kFw1qXp6uIUir5qy6lMNvejGlDKZ0NB7NGH3u8ZFUTYFcMa90PyBXMrDy9SBng5v5cjZ7uhLYSslJRUqtCqnrgrOTcsVkViQLHY%2FK8ygc%2ByYZbKK92QqjlEHdjKqYSeOe7Tsl1PWefw6hhPX8hcykPX3h%2BhISa7aL47oaGb5TNYXHW6ujUxGd8jpQBNGp7OzDtkhVNYnI2%2Bz2SdVS0JPN9jeGadUs4t3k%2BpN6QmoI0vNsrlpWwqLh080MJpG19GgSSRPsHSlV86J3StPGxpNEk8RqmacZRPY3TFS%2BKIo4olZN9Ub64vap2tIIPll4arBiciEzXVO4tquaXI6k%2Bf%2BDRPI7IpF4TVQxnR010Xvl0LU2k88pbMNbr5i95os0dpAWqYUWI7DKqeS78W1bktPWxubYVqmPD%2FjwmJqZm1paJbPwSwwCNXrnazz3UYHnvoAWW0hT%2BhBMXJCAQVpI9CczubMcm7CaXqVQVlUBE1RtS%2Fxiave2ojL%2FaIM4%2BNQsfOkPJciqiOUnbEtpHL5bWxQsWmGrIQB5LWk%2FVRCg4r9%2BfG8LiIRLcTQLp5pOgAiCU%2FzyMPe2PvEDtCH7Jk4wqAXwRYYbhTf9eThR8IpfjfreVo56dPYHWgNbLWwHnAP9iAypj678RLvpHNwLJnmuAfu2gLEFjlU3%2FKqShH%2BoCYCf7LqYvvs58UBXk%2FmCTbrW3uy%2F%3C%2Fdiagram%3E%3C%2Fmxfile%3E)

**Supporting explanation document:** [business_process_explanation.pdf](docs/business_process/business_process_explanation.pdf)

**Diagram PDF:** [business_process_diagram.pdf](docs/business_process/business_process_diagram.pdf)
