"""PitchGuard data preparation: SoccerMon subjective data -> clean tables for Oracle.

Usage:
    python clean_data.py <path to unzipped 'subjective' folder> <output folder>

Reads the raw SoccerMon files (wide grids, JSON, dd.mm.yyyy dates) and writes
one CSV per planned table with ISO dates (YYYY-MM-DD), ready to load into Oracle.
Dataset: Midoglu et al. (2022), https://doi.org/10.5281/zenodo.10033832 (CC BY 4.0)
"""
import json
import sys
from pathlib import Path

import pandas as pd

WELLNESS = {  # file name -> column in WELLNESS_REPORT
    "fatigue.csv": "fatigue",
    "mood.csv": "mood",
    "readiness.csv": "readiness",
    "sleep_duration.csv": "sleep_duration_h",
    "sleep_quality.csv": "sleep_quality",
    "soreness.csv": "soreness",
    "stress.csv": "stress",
}


def iso(series):
    """dd.mm.yyyy -> YYYY-MM-DD"""
    return pd.to_datetime(series, format="%d.%m.%Y").dt.strftime("%Y-%m-%d")


def main(src, out):
    src, out = Path(src), Path(out)
    out.mkdir(parents=True, exist_ok=True)

    # ---- TEAM and PLAYER (from the anonymized player codes) ----
    sessions = json.loads((src / "training-load" / "session.json").read_text())
    codes = list(sessions.keys())
    team_names = sorted({c.split("-", 1)[0] for c in codes})
    team = pd.DataFrame({"team_id": range(1, len(team_names) + 1), "team_name": team_names})
    team_id = dict(zip(team.team_name, team.team_id))
    player = pd.DataFrame({"player_id": range(1, len(codes) + 1), "player_code": codes})
    player["team_id"] = player.player_code.str.split("-", n=1).str[0].map(team_id)
    pid = dict(zip(player.player_code, player.player_id))

    # ---- SESSION_LOAD (one row per player session) ----
    rows = [
        (pid[code], s["date"], s["rpe"], s["duration"], s["srpe"])
        for code, lst in sessions.items()
        for s in lst
    ]
    load = pd.DataFrame(rows, columns=["player_id", "session_date", "rpe", "duration_min", "srpe"])
    load["session_date"] = iso(load.session_date)
    load = load.sort_values(["player_id", "session_date"]).reset_index(drop=True)
    load.insert(0, "load_id", range(1, len(load) + 1))

    # ---- WELLNESS_REPORT (unpivot 7 wide grids, merge on player + date) ----
    merged = None
    for fname, col in WELLNESS.items():
        grid = pd.read_csv(src / "wellness" / fname)
        grid = grid.rename(columns={grid.columns[0]: "report_date"})
        long = grid.melt(id_vars="report_date", var_name="player_code", value_name=col).dropna(subset=[col])
        merged = long if merged is None else merged.merge(long, on=["report_date", "player_code"], how="outer")
    merged["player_id"] = merged.player_code.map(pid)
    merged["report_date"] = iso(merged.report_date)
    wellness = merged.drop(columns="player_code").sort_values(["player_id", "report_date"]).reset_index(drop=True)
    wellness.insert(0, "wellness_id", range(1, len(wellness) + 1))
    wellness = wellness[["wellness_id", "player_id", "report_date", "fatigue", "mood", "readiness",
                         "sleep_duration_h", "sleep_quality", "soreness", "stress"]]

    # ---- INJURY (parse JSON: body location -> severity) ----
    inj = pd.read_csv(src / "injury" / "injury.csv")
    recs = []
    for _, r in inj.iterrows():
        for loc, sev in json.loads(r["type"]).items():
            recs.append((pid[r.player_name], r.timestamp, loc, sev))
    injury = pd.DataFrame(recs, columns=["player_id", "report_date", "body_location", "severity"])
    injury["report_date"] = iso(injury.report_date)
    injury = injury.drop_duplicates().sort_values(["player_id", "report_date"]).reset_index(drop=True)
    injury.insert(0, "injury_id", range(1, len(injury) + 1))

    # ---- ILLNESS (optional table) ----
    ill = pd.read_csv(src / "illness" / "illness.csv")
    recs = [(pid[r.player_name], r.timestamp, p) for _, r in ill.iterrows() for p in json.loads(r["problems"])]
    illness = pd.DataFrame(recs, columns=["player_id", "report_date", "problem"])
    illness["report_date"] = iso(illness.report_date)
    illness.insert(0, "illness_id", range(1, len(illness) + 1))

    # ---- GAME_PERFORMANCE (optional table) ----
    gp = pd.read_csv(src / "game-performance" / "game-performance.csv")
    gp["player_id"] = gp.player_name.map(pid)
    gp["match_date"] = iso(gp.timestamp)
    gp = gp.rename(columns={"team_performance": "team_perf", "offensive_performance": "offensive_perf",
                            "defensive_performance": "defensive_perf"})
    gp = gp[["player_id", "match_date", "team_perf", "offensive_perf", "defensive_perf"]]
    gp = gp.sort_values(["player_id", "match_date"]).reset_index(drop=True)
    gp.insert(0, "performance_id", range(1, len(gp) + 1))

    for name, df in [("team", team), ("player", player), ("session_load", load), ("wellness_report", wellness),
                     ("injury", injury), ("illness", illness), ("game_performance", gp)]:
        df.to_csv(out / f"{name}.csv", index=False)
        print(f"{name}.csv: {len(df)} rows")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
