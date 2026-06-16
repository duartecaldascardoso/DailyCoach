#!/usr/bin/env python3
"""Import historical Strava activities into the DailyCoach data structure."""

import json
import os
from datetime import date, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
WEEKS = os.path.join(DATA, "weeks")


def format_pace(moving_sec, dist_m):
    if not dist_m or dist_m <= 0 or not moving_sec or moving_sec <= 0:
        return None
    secs = moving_sec / (dist_m / 1000)
    m = int(secs // 60)
    s = int(round(secs % 60))
    if s == 60:
        m += 1
        s = 0
    return f"{m}:{s:02d}"


def classify_run(dist_m, moving_sec, hr_avg):
    if not dist_m or dist_m <= 0:
        return None
    dist_km = dist_m / 1000
    if dist_km >= 12:
        return "long"
    pace_secs = (moving_sec / dist_km) if dist_km > 0 else 999
    if hr_avg and hr_avg >= 175:
        return "tempo"
    if pace_secs < 315:  # faster than 5:15/km
        return "tempo"
    if pace_secs > 430 or (hr_avg and hr_avg < 150 and pace_secs > 380):
        return "recovery"
    return "easy"


def day_name(d):
    return ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"][d.weekday()]


def get_week_id(d):
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def week_bounds(d):
    iso = d.isocalendar()
    year, week = iso[0], iso[1]
    jan4 = date(year, 1, 4)
    w1_mon = jan4 - timedelta(days=jan4.weekday())
    start = w1_mon + timedelta(weeks=week - 1)
    end = start + timedelta(days=6)
    return start, end


# ---------------------------------------------------------------------------
# All Strava activities from the export
# Keys: id, date, name, atype (Strava type), elapsed, moving, dist (m),
#       hr_max, hr_avg, elev (m), shoes, gym_type (if gym activity)
# ---------------------------------------------------------------------------
ACTIVITIES = [
    # W25 - new
    {"id": "18942451658", "date": "2026-06-16", "name": "Corrida da hora do almoço",
     "atype": "run", "elapsed": 2015, "moving": 2008, "dist": 5009.6,
     "hr_max": 166, "hr_avg": 154, "elev": 30.2, "shoes": "Nike Vomero Plus"},

    # W24 - existing (update only)
    {"id": "18916147714", "date": "2026-06-14", "name": "Corrida matinal",
     "atype": "run", "elapsed": 7055, "moving": 6636, "dist": 17585.8,
     "hr_max": 182, "hr_avg": 167, "elev": 106, "shoes": "Nike Vomero Plus"},
    {"id": "18900494384", "date": "2026-06-13", "name": "Ombros e abdominal",
     "atype": "gym", "elapsed": 2366, "moving": 2366, "dist": 0,
     "hr_max": 150, "hr_avg": 113, "elev": 0, "shoes": None, "gym_type": "shoulders+abs"},
    {"id": "18894434634", "date": "2026-06-12", "name": "Vólei de praia",
     "atype": "volleyball", "elapsed": 4320, "moving": 4320, "dist": 0,
     "hr_max": None, "hr_avg": None, "elev": 0, "shoes": None},
    {"id": "18893459548", "date": "2026-06-12", "name": "Treino com pesos ao entardecer",
     "atype": "gym", "elapsed": 1511, "moving": 1511, "dist": 0,
     "hr_max": 150, "hr_avg": 107, "elev": 0, "shoes": None, "gym_type": "general"},
    {"id": "18881531310", "date": "2026-06-11", "name": "Corrida ao entardecer",
     "atype": "run", "elapsed": 1679, "moving": 1441, "dist": 5000.7,
     "hr_max": 194, "hr_avg": 180, "elev": 16.2, "shoes": None},
    {"id": "18854501547", "date": "2026-06-09", "name": "Corrida ao entardecer",
     "atype": "run", "elapsed": 2524, "moving": 2524, "dist": 6009.3,
     "hr_max": 165, "hr_avg": 153, "elev": 23.2, "shoes": None},
    {"id": "18839317413", "date": "2026-06-08", "name": "Easy run com a brownie",
     "atype": "run", "elapsed": 1428, "moving": 1391, "dist": 3379.5,
     "hr_max": 173, "hr_avg": 154, "elev": 26.8, "shoes": None},

    # W23 - existing (update only)
    {"id": "18821431306", "date": "2026-06-07", "name": "Caminho para trás com a maior",
     "atype": "walk", "elapsed": 1422, "moving": 1422, "dist": 1766.4,
     "hr_max": 133, "hr_avg": 106, "elev": 3, "shoes": None},
    {"id": "18821431329", "date": "2026-06-07", "name": "Easy run",
     "atype": "run", "elapsed": 1290, "moving": 1257, "dist": 3317.9,
     "hr_max": 175, "hr_avg": 162, "elev": 7.6, "shoes": None},
    {"id": "18808585021", "date": "2026-06-06", "name": "Primeira corrida da maior",
     "atype": "run", "elapsed": 1448, "moving": 1386, "dist": 3007.8,
     "hr_max": 167, "hr_avg": 151, "elev": 8.6, "shoes": None},
    {"id": "18807962821", "date": "2026-06-06", "name": "Treino com pesos na hora de almoço",
     "atype": "gym", "elapsed": 1685, "moving": 1685, "dist": 0,
     "hr_max": 154, "hr_avg": 112, "elev": 0, "shoes": None, "gym_type": "general"},
    {"id": "18799363746", "date": "2026-06-05", "name": "Corrida vespertina",
     "atype": "run", "elapsed": 1240, "moving": 1235, "dist": 4002.6,
     "hr_max": 181, "hr_avg": 173, "elev": 30.4, "shoes": None},
    {"id": "18780859933", "date": "2026-06-04", "name": "Corrida com a Brownie",
     "atype": "run", "elapsed": 1426, "moving": 1394, "dist": 3605.1,
     "hr_max": 177, "hr_avg": 163, "elev": 35, "shoes": None},

    # W22 - new week
    {"id": "18727162033", "date": "2026-05-31", "name": "Corrida matinal",
     "atype": "run", "elapsed": 5721, "moving": 5597, "dist": 15008.7,
     "hr_max": 189, "hr_avg": 178, "elev": 56.2, "shoes": None},
    {"id": "18691643322", "date": "2026-05-28", "name": "Corrida vespertina",
     "atype": "run", "elapsed": 1458, "moving": 1373, "dist": 4009.7,
     "hr_max": 184, "hr_avg": 176, "elev": 9, "shoes": None},
    {"id": "18691224624", "date": "2026-05-28", "name": "Peito e triceps",
     "atype": "gym", "elapsed": 1834, "moving": 1834, "dist": 0,
     "hr_max": 152, "hr_avg": 107, "elev": 0, "shoes": None, "gym_type": "chest+triceps"},
    {"id": "18663296613", "date": "2026-05-26", "name": "Easy run",
     "atype": "run", "elapsed": 1804, "moving": 1793, "dist": 3789,
     "hr_max": 158, "hr_avg": 144, "elev": 32, "shoes": None},
    {"id": "18652021201", "date": "2026-05-25", "name": "Corrida ao entardecer",
     "atype": "run", "elapsed": 1344, "moving": 1338, "dist": 4260,
     "hr_max": 201, "hr_avg": 186, "elev": 3.7, "shoes": None},
    {"id": "18651422917", "date": "2026-05-25", "name": "Costas e bíceps",
     "atype": "gym", "elapsed": 1742, "moving": 1742, "dist": 0,
     "hr_max": None, "hr_avg": None, "elev": 0, "shoes": None, "gym_type": "back+biceps"},

    # W21 - new week
    {"id": "18633862759", "date": "2026-05-24", "name": "Surfzinho",
     "atype": "surf", "elapsed": 2796, "moving": 1767, "dist": 1199.4,
     "hr_max": None, "hr_avg": None, "elev": 0, "shoes": None},
    {"id": "18558982766", "date": "2026-05-18", "name": "Corrida ao entardecer",
     "atype": "run", "elapsed": 1717, "moving": 1606, "dist": 5008.2,
     "hr_max": 190, "hr_avg": 178, "elev": 2.3, "shoes": None},

    # W20 - new week
    {"id": "18541493973", "date": "2026-05-17", "name": "Sunday Lunch Run",
     "atype": "run", "elapsed": 1749, "moving": 1585, "dist": 5005.8,
     "hr_max": 196, "hr_avg": 175, "elev": 5.3, "shoes": None},

    # W19 - new week
    {"id": "18411508847", "date": "2026-05-07", "name": "Treino com pesos na hora de almoço",
     "atype": "gym", "elapsed": 2273, "moving": 2273, "dist": 0,
     "hr_max": 158, "hr_avg": 116, "elev": 0, "shoes": None, "gym_type": "general"},
    {"id": "18386109950", "date": "2026-05-05", "name": "Cortejo",
     "atype": "run", "elapsed": 959, "moving": 138, "dist": 498.8,
     "hr_max": None, "hr_avg": None, "elev": 0, "shoes": None},

    # W18 - new week
    {"id": "18323607518", "date": "2026-04-30", "name": "Corrida noturna",
     "atype": "run", "elapsed": 309, "moving": 281, "dist": 521,
     "hr_max": None, "hr_avg": None, "elev": 0, "shoes": None},
    {"id": "18309364294", "date": "2026-04-29", "name": "Corrida ao anoitecer",
     "atype": "run", "elapsed": 2009, "moving": 1979, "dist": 5764.4,
     "hr_max": None, "hr_avg": None, "elev": 31.3, "shoes": None},

    # W17 - new week
    {"id": "18186606135", "date": "2026-04-20", "name": "Monday Afternoon Run",
     "atype": "run", "elapsed": 1166, "moving": 843, "dist": 2532.5,
     "hr_max": None, "hr_avg": None, "elev": 2.3, "shoes": None},

    # W16 - new week
    {"id": "18122988823", "date": "2026-04-15", "name": "Volta de bicicleta ao anoitecer",
     "atype": "bike", "elapsed": 3040, "moving": 2435, "dist": 13430.9,
     "hr_max": None, "hr_avg": None, "elev": 42.7, "shoes": None},

    # W14 - new week
    {"id": "17960957410", "date": "2026-04-03", "name": "com o brother",
     "atype": "run", "elapsed": 2405, "moving": 2394, "dist": 6753.7,
     "hr_max": None, "hr_avg": None, "elev": 14.9, "shoes": None},
    {"id": "17928838420", "date": "2026-03-31", "name": "Tuesday Evening Run",
     "atype": "run", "elapsed": 3723, "moving": 3540, "dist": 10015,
     "hr_max": None, "hr_avg": None, "elev": 23.5, "shoes": None},

    # W13 - new week
    {"id": "17844499629", "date": "2026-03-24", "name": "Tuesday Evening Run",
     "atype": "run", "elapsed": 1512, "moving": 1218, "dist": 3522.6,
     "hr_max": None, "hr_avg": None, "elev": 4.4, "shoes": None},

    # W12 - new week
    {"id": "17802129041", "date": "2026-03-21", "name": "Saturday Lunch Run",
     "atype": "run", "elapsed": 3064, "moving": 2480, "dist": 7273.5,
     "hr_max": None, "hr_avg": None, "elev": 13.9, "shoes": None},
    {"id": "17758074629", "date": "2026-03-17", "name": "Tuesday Evening Run",
     "atype": "run", "elapsed": 1328, "moving": 1264, "dist": 4027.4,
     "hr_max": None, "hr_avg": None, "elev": 4.7, "shoes": None},

    # W11 - new week
    {"id": "17730539983", "date": "2026-03-15", "name": "Sunday Lunch Run",
     "atype": "run", "elapsed": 1815, "moving": 1694, "dist": 4712.1,
     "hr_max": None, "hr_avg": None, "elev": 12.1, "shoes": None},
    {"id": "17675599148", "date": "2026-03-10", "name": "Bom pace mas fiquei todo roto",
     "atype": "run", "elapsed": 694, "moving": 691, "dist": 2162.3,
     "hr_max": None, "hr_avg": None, "elev": 2.4, "shoes": None},

    # W10 - new week
    {"id": "17635989022", "date": "2026-03-07", "name": "Primeiros 10k",
     "atype": "run", "elapsed": 3993, "moving": 3937, "dist": 10002.5,
     "hr_max": None, "hr_avg": None, "elev": 18.6, "shoes": None},
    {"id": "17592569289", "date": "2026-03-03", "name": "Corrida ao anoitecer",
     "atype": "run", "elapsed": 2514, "moving": 2485, "dist": 6380.7,
     "hr_max": None, "hr_avg": None, "elev": 11.2, "shoes": None},

    # W9 - new week
    {"id": "17555903579", "date": "2026-02-28", "name": "Corrida vespertina",
     "atype": "run", "elapsed": 1415, "moving": 1406, "dist": 3678.8,
     "hr_max": None, "hr_avg": None, "elev": 38.7, "shoes": None},
    # Feb 24 had two short runs - combined here as one session
    {"id": "17509251820,17509482441", "date": "2026-02-24", "name": "Corrida ao anoitecer",
     "atype": "run",
     "elapsed": 662 + 838, "moving": 662 + 822, "dist": 2042.6 + 2075.1,
     "hr_max": None, "hr_avg": None, "elev": max(2.4, 2.1), "shoes": None},
]

# Weeks that already exist in the repo (don't create week.json for these)
EXISTING_WEEKS = {"2026-W23", "2026-W24", "2026-W25"}

# Days that already exist (update rather than create)
EXISTING_DAYS = {
    "2026-06-04", "2026-06-05", "2026-06-06", "2026-06-07",
    "2026-06-08", "2026-06-09", "2026-06-11", "2026-06-12",
    "2026-06-13", "2026-06-14",
}


def build_activity_obj(act):
    """Build the activity JSON object for a day file."""
    atype = act["atype"]
    if atype == "run":
        dist_km = round(act["dist"] / 1000, 1) if act["dist"] else None
        pace = format_pace(act["moving"], act["dist"])
        dur = round(act["elapsed"] / 60)
        run_type = classify_run(act["dist"], act["moving"], act.get("hr_avg"))
        return {
            "type": "run",
            "run_type": run_type,
            "distance_km": dist_km,
            "pace_per_km": pace,
            "duration_minutes": dur,
            "heart_rate_avg": act.get("hr_avg"),
            "heart_rate_max": act.get("hr_max"),
            "elevation_m": round(act["elev"], 1) if act["elev"] else None,
            "shoes": act.get("shoes"),
            "strava_activity_id": act["id"],
        }
    elif atype == "bike":
        dist_km = round(act["dist"] / 1000, 1) if act["dist"] else None
        dur = round(act["elapsed"] / 60)
        return {
            "type": "bike",
            "run_type": None,
            "distance_km": dist_km,
            "pace_per_km": None,
            "duration_minutes": dur,
            "heart_rate_avg": act.get("hr_avg"),
            "heart_rate_max": act.get("hr_max"),
            "elevation_m": round(act["elev"], 1) if act["elev"] else None,
            "shoes": None,
            "strava_activity_id": act["id"],
        }
    elif atype == "volleyball":
        dur = round(act["elapsed"] / 60)
        return {
            "type": "volleyball",
            "run_type": None,
            "distance_km": None,
            "pace_per_km": None,
            "duration_minutes": dur,
            "heart_rate_avg": None,
            "heart_rate_max": None,
            "elevation_m": None,
            "shoes": None,
            "strava_activity_id": act["id"],
        }
    elif atype == "surf":
        dur = round(act["elapsed"] / 60)
        dist_km = round(act["dist"] / 1000, 1) if act["dist"] else None
        return {
            "type": "surf",
            "run_type": None,
            "distance_km": dist_km,
            "pace_per_km": None,
            "duration_minutes": dur,
            "heart_rate_avg": None,
            "heart_rate_max": None,
            "elevation_m": None,
            "shoes": None,
            "strava_activity_id": act["id"],
        }
    elif atype == "walk":
        dur = round(act["elapsed"] / 60)
        dist_km = round(act["dist"] / 1000, 1) if act["dist"] else None
        return {
            "type": "walk",
            "run_type": None,
            "distance_km": dist_km,
            "pace_per_km": None,
            "duration_minutes": dur,
            "heart_rate_avg": act.get("hr_avg"),
            "heart_rate_max": act.get("hr_max"),
            "elevation_m": round(act["elev"], 1) if act["elev"] else None,
            "shoes": None,
            "strava_activity_id": act["id"],
        }
    return None


def build_gym_obj(act):
    """Build the gym JSON object from a gym activity."""
    dur = round(act["elapsed"] / 60)
    return {
        "completed": True,
        "type": act.get("gym_type", "general"),
        "duration_minutes": dur,
        "notes": "",
        "strava_activity_id": act["id"],
    }


def build_new_day(act_date_str, acts_for_day, week_id):
    """Build a brand-new day JSON for a historical date."""
    d = date.fromisoformat(act_date_str)

    # Separate by type
    runs = [a for a in acts_for_day if a["atype"] == "run"]
    gyms = [a for a in acts_for_day if a["atype"] == "gym"]
    others = [a for a in acts_for_day if a["atype"] not in ("run", "gym")]

    # Primary activity: run > bike > volleyball > surf > walk > gym
    primary_order = ["run", "bike", "volleyball", "surf", "walk"]
    primary = None
    for ptype in primary_order:
        candidates = [a for a in acts_for_day if a["atype"] == ptype]
        if candidates:
            primary = max(candidates, key=lambda x: x["dist"])
            break

    activity_obj = build_activity_obj(primary) if primary else None
    gym_obj = build_gym_obj(gyms[0]) if gyms else None

    return {
        "date": act_date_str,
        "day_of_week": day_name(d),
        "week_id": week_id,
        "planned": None,
        "completed": True,
        "activity": activity_obj,
        "gym": gym_obj,
        "daily_comment": None,
    }


def update_existing_day(filepath, acts_for_day):
    """Update an existing day JSON with Strava data (IDs, HR, shoes)."""
    with open(filepath) as f:
        data = json.load(f)

    runs = [a for a in acts_for_day if a["atype"] == "run"]
    gyms = [a for a in acts_for_day if a["atype"] == "gym"]
    walks = [a for a in acts_for_day if a["atype"] == "walk"]
    volleyballs = [a for a in acts_for_day if a["atype"] == "volleyball"]

    # Update activity strava data
    if data.get("activity") and runs:
        r = max(runs, key=lambda x: x["dist"])
        data["activity"]["strava_activity_id"] = r["id"]
        if data["activity"].get("heart_rate_avg") is None and r.get("hr_avg"):
            data["activity"]["heart_rate_avg"] = r["hr_avg"]
        if data["activity"].get("heart_rate_max") is None and r.get("hr_max"):
            data["activity"]["heart_rate_max"] = r["hr_max"]
        if data["activity"].get("shoes") is None and r.get("shoes"):
            data["activity"]["shoes"] = r["shoes"]

    # For volleyball-only days
    if data.get("activity") and data["activity"].get("type") == "volleyball" and volleyballs:
        v = volleyballs[0]
        data["activity"]["strava_activity_id"] = v["id"]

    # Add gym if missing
    if data.get("gym") is None and gyms:
        data["gym"] = build_gym_obj(gyms[0])
    elif data.get("gym") and gyms:
        if not data["gym"].get("strava_activity_id"):
            data["gym"]["strava_activity_id"] = gyms[0]["id"]
        if data["gym"].get("heart_rate_max") is None and gyms[0].get("hr_max"):
            data["gym"]["heart_rate_max"] = gyms[0]["hr_max"]

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return data


def write_week_json(week_id):
    """Write a minimal week.json for a historical week."""
    start, end = week_bounds(date.fromisoformat(
        [a["date"] for a in ACTIVITIES if get_week_id(date.fromisoformat(a["date"])) == week_id][0]
    ))
    return {
        "week_id": week_id,
        "start_date": str(start),
        "end_date": str(end),
        "plan": None,
        "review": None,
        "created_at": "2026-06-16T00:00:00Z",
        "reviewed_at": None,
    }


def main():
    os.makedirs(WEEKS, exist_ok=True)

    # Group activities by date
    by_date = {}
    for act in ACTIVITIES:
        by_date.setdefault(act["date"], []).append(act)

    # Track what we create for manifest update
    week_days = {}  # week_id -> [day_stem, ...]

    for act_date_str, acts in sorted(by_date.items()):
        d = date.fromisoformat(act_date_str)
        week_id = get_week_id(d)
        week_dir = os.path.join(WEEKS, week_id)
        os.makedirs(week_dir, exist_ok=True)

        day_stem = f"{act_date_str}-{day_name(d)[:3]}"
        filepath = os.path.join(week_dir, f"{act_date_str}-{day_name(d)[:3]}.json")

        if act_date_str in EXISTING_DAYS:
            update_existing_day(filepath, acts)
            print(f"  UPDATED  {filepath}")
        else:
            day_data = build_new_day(act_date_str, acts, week_id)
            with open(filepath, "w") as f:
                json.dump(day_data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"  CREATED  {filepath}")

        week_days.setdefault(week_id, []).append(day_stem)

    # Write week.json for new weeks
    for week_id in sorted(week_days):
        if week_id in EXISTING_WEEKS:
            continue
        week_dir = os.path.join(WEEKS, week_id)
        week_file = os.path.join(week_dir, "week.json")
        week_data = write_week_json(week_id)
        with open(week_file, "w") as f:
            json.dump(week_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  CREATED  {week_file}")

    # Update manifest.json
    manifest_path = os.path.join(DATA, "manifest.json")
    with open(manifest_path) as f:
        manifest = json.load(f)

    existing_week_ids = {w["week_id"] for w in manifest["weeks"]}

    # Add new weeks to manifest
    for week_id in sorted(week_days):
        if week_id not in existing_week_ids:
            sample_date = date.fromisoformat(
                [a["date"] for a in ACTIVITIES if get_week_id(date.fromisoformat(a["date"])) == week_id][0]
            )
            start, end = week_bounds(sample_date)
            manifest["weeks"].append({
                "week_id": week_id,
                "start_date": str(start),
                "end_date": str(end),
                "has_review": False,
                "days": sorted(week_days[week_id]),
            })

    # Update day lists for existing weeks
    for w in manifest["weeks"]:
        if w["week_id"] in week_days:
            new_days = week_days[w["week_id"]]
            combined = sorted(set(w.get("days", []) + new_days))
            w["days"] = combined

    # Sort weeks chronologically
    manifest["weeks"] = sorted(manifest["weeks"], key=lambda x: x["week_id"])
    manifest["updated_at"] = "2026-06-16T13:30:00Z"

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"  UPDATED  {manifest_path}")

    # Update activities.json with today's run
    activities_path = os.path.join(DATA, "activities.json")
    with open(activities_path) as f:
        acts_data = json.load(f)

    today_run = next((a for a in ACTIVITIES if a["date"] == "2026-06-16" and a["atype"] == "run"), None)
    if today_run:
        new_entry = {
            "date": "2026-06-16",
            "name": today_run["name"],
            "distance_km": round(today_run["dist"] / 1000, 1),
            "pace_per_km": format_pace(today_run["moving"], today_run["dist"]),
            "duration_minutes": round(today_run["elapsed"] / 60),
            "elevation_m": round(today_run["elev"]),
            "type": classify_run(today_run["dist"], today_run["moving"], today_run.get("hr_avg")),
            "strava_activity_id": today_run["id"],
        }
        acts_data["recent_activities"].insert(0, new_entry)
        acts_data["recent_activities"] = acts_data["recent_activities"][:10]

    acts_data["updated_at"] = "2026-06-16T13:30:00Z"
    acts_data["week_summary"] = {
        "total_distance_km": round(today_run["dist"] / 1000, 1) if today_run else 0,
        "total_runs": 1 if today_run else 0,
        "total_elevation_m": round(today_run["elev"]) if today_run else 0,
        "total_time_minutes": round(today_run["elapsed"] / 60) if today_run else 0,
    }

    with open(activities_path, "w") as f:
        json.dump(acts_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"  UPDATED  {activities_path}")

    print("\nDone! Summary:")
    print(f"  Weeks processed: {sorted(week_days.keys())}")


if __name__ == "__main__":
    main()
