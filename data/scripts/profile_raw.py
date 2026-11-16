import json, re, sys
from pathlib import Path
from collections import Counter
import pandas as pd

src = Path(sys.argv[1])
DATE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
def ok_date(s):
    try:
        pd.to_datetime(s, format="%d.%m.%Y"); return bool(DATE.match(str(s)))
    except Exception: return False

sess = json.loads((src/"training-load"/"session.json").read_text())
players = set(sess)
print("PLAYERS in session.json:", len(players), Counter(p.split('-')[0] for p in players))

def grid(path):
    df = pd.read_csv(path)
    first = df.columns[0]
    cols = list(df.columns[1:])
    vals = df[cols]
    nonnum = 0
    for c in cols:
        s = vals[c]
        nn = pd.to_numeric(s, errors="coerce")
        nonnum += int((s.notna() & nn.isna()).sum())
    num = vals.apply(pd.to_numeric, errors="coerce")
    n_cells = vals.size
    filled = int(vals.notna().sum().sum())
    bad_dates = int((~df[first].astype(str).map(ok_date)).sum())
    dup_dates = int(df[first].duplicated().sum())
    return dict(first=first, rows=len(df), players=len(cols), same_players=set(cols)==players,
                cells=n_cells, filled=filled, empty=n_cells-filled, nonnumeric=nonnum,
                vmin=float(num.min().min()), vmax=float(num.max().max()),
                bad_dates=bad_dates, dup_dates=dup_dates,
                d0=df[first].iloc[0], d1=df[first].iloc[-1])

print("\n== GRID FILES")
for sub in ["wellness","training-load"]:
    for f in sorted((src/sub).glob("*.csv")):
        g = grid(f); print(sub, f.name, g)

print("\n== session.json")
rows = [(p, s.get("date"), s.get("rpe"), s.get("duration"), s.get("srpe")) for p, l in sess.items() for s in l]
df = pd.DataFrame(rows, columns=["p","date","rpe","dur","srpe"])
print("sessions", len(df))
print("missing fields", df.isna().sum().to_dict())
print("types", Counter(type(x).__name__ for l in sess.values() for s in l for x in s.values()))
print("bad dates", int((~df.date.map(ok_date)).sum()))
print("rpe range", df.rpe.min(), df.rpe.max(), "dur range", df.dur.min(), df.dur.max(), "srpe range", df.srpe.min(), df.srpe.max())
print("srpe != rpe*dur", int((df.srpe != df.rpe*df.dur).sum()))
print("rpe==0 or dur==0", int(((df.rpe==0)|(df.dur==0)).sum()), "dur>180", int((df.dur>180).sum()))
print("exact duplicate sessions (same player,date,rpe,dur)", int(df.duplicated().sum()))
print("player-days with >1 session", int((df.groupby(["p","date"]).size()>1).sum()), "max sessions/day", int(df.groupby(["p","date"]).size().max()))
print("sessions/player min,max", df.groupby("p").size().min(), df.groupby("p").size().max())
dd = pd.to_datetime(df.date, format="%d.%m.%Y")
print("date range", dd.min().date(), dd.max().date())

print("\n== injury.csv")
inj = pd.read_csv(src/"injury"/"injury.csv")
print("rows", len(inj), "missing", inj.isna().sum().to_dict())
print("exact duplicate rows", int(inj.duplicated().sum()))
print("bad dates", int((~inj.timestamp.map(ok_date)).sum()))
print("players not in session.json", int((~inj.player_name.isin(players)).sum()), "distinct players", inj.player_name.nunique())
locs=Counter(); sev=Counter(); multi=0; empty=0; badjson=0
exp=[]
for _, r in inj.iterrows():
    try: d=json.loads(r["type"])
    except Exception: badjson+=1; continue
    if not d: empty+=1
    if len(d)>1: multi+=1
    for k,v in d.items(): locs[k]+=1; sev[v]+=1; exp.append((r.player_name,r.timestamp,k,v))
print("bad json", badjson, "empty json", empty, "rows with >1 location", multi)
print("locations", len(locs), dict(locs)); print("severity values", dict(sev))
e=pd.DataFrame(exp, columns=["p","d","loc","sev"])
print("expanded injury records", len(e), "duplicates after expansion", int(e.duplicated().sum()), "unique", len(e.drop_duplicates()))
print("same player/date/location, conflicting severity", int((e.drop_duplicates().groupby(["p","d","loc"]).sev.nunique()>1).sum()))

print("\n== illness.csv")
il = pd.read_csv(src/"illness"/"illness.csv")
print("rows", len(il), "dups", int(il.duplicated().sum()), "bad dates", int((~il.timestamp.map(ok_date)).sum()))
pr=Counter(); n=0
for x in il.problems:
    L=json.loads(x); n+=len(L); pr.update(L)
print("problem entries", n, dict(pr))

print("\n== game-performance.csv")
gp = pd.read_csv(src/"game-performance"/"game-performance.csv")
print("rows", len(gp), "missing", gp.isna().sum().to_dict(), "dups", int(gp.duplicated().sum()))
print("bad dates", int((~gp.timestamp.map(ok_date)).sum()), "players", gp.player_name.nunique(), "not in session", int((~gp.player_name.isin(players)).sum()))
print(gp[["team_performance","offensive_performance","defensive_performance"]].agg(["min","max"]).to_dict())
print("same player+date twice", int(gp.duplicated(["player_name","timestamp"]).sum()))

print("\n== extra checks")
for f in sorted(src.glob("*/*")):
    b = f.read_bytes()
    print(f.relative_to(src), "CRLF" if b"\r\n" in b else "LF")
W = {"fatigue", "mood", "readiness", "sleep_duration", "sleep_quality", "soreness", "stress"}
cnt = None
for k in sorted(W):
    g = pd.read_csv(src/"wellness"/f"{k}.csv"); g = g.rename(columns={g.columns[0]: "d"})
    l = g.melt(id_vars="d").dropna(subset=["value"])
    if k == "sleep_duration":
        print("sleep_duration non-integer", int((l.value % 1 != 0).sum()), "of", len(l))
    l = l.rename(columns={"value": k})[["d", "variable", k]]
    cnt = l if cnt is None else cnt.merge(l, on=["d", "variable"], how="outer")
m = cnt.drop(columns=["d", "variable"]).notna().sum(axis=1)
print("wellness player-days", len(cnt), "complete", int((m == 7).sum()), "incomplete", int((m < 7).sum()), m.value_counts().sort_index().to_dict())
print("distinct sessions-days: player-days with a session", len(df[["p", "date"]].drop_duplicates()))
print("longest sessions", sorted(df.dur.unique())[-3:])
dl = pd.read_csv(src/"training-load"/"daily_load.csv").iloc[:, 1:]
print("daily_load zero cells", int((dl == 0).sum().sum()), "nonzero", int((dl > 0).sum().sum()))
