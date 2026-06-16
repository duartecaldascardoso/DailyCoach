# Daily Training Routine — Every day at 8am

Paste this as the prompt when creating your Claude routine at claude.ai/code/routines.
Set the trigger to **daily at 08:00 (local time)**. Include the **Strava** and **Google Calendar** connectors.

---

## Context

- **Athlete**: Duarte Cardoso, training for distance running
- **Goal A**: Half Marathon, Porto, 13 September 2026
- **Goal B**: Marathon, Porto, 8 November 2026
- **Repo**: This GitHub Pages repo at `data/weeks/` stores all training data
- **Week format**: ISO weeks (Monday–Sunday), folder named `YYYY-WXX`

---

## Step 1 — Determine yesterday and the current week

Calculate yesterday's date and its ISO week ID.
Read `data/manifest.json` to find the current week folder.
Read `data/weeks/{week-id}/week.json` to get the plan.

Find yesterday's planned session from the `plan.sessions` array (match by day name: monday, tuesday, etc.).

---

## Step 2 — Fetch Strava data for yesterday

Use the Strava connector to check for activities on yesterday's date.

If a run was recorded, extract:
- `distance_km` (1 decimal)
- `pace_per_km` (format M:SS)
- `duration_minutes` (integer)
- `heart_rate_avg` (integer, if available from HR monitor)
- `heart_rate_max` (integer, if available)
- `elevation_m` (integer)
- `shoes` (from Strava gear data, e.g. "Nike Pegasus 41")
- `strava_activity_id`

Classify the run type as one of: `easy` | `tempo` | `long` | `interval` | `race` | `recovery`
- **long**: ≥14 km
- **interval**: short with fast segments, or matches "interval/VO2max" in plan
- **tempo**: sustained effort near threshold (pace ≤5:30/km for 4+ km)
- **easy**: conversational pace (≥6:00/km)
- **recovery**: very short and slow (≤4 km at ≥6:30/km)
- **race**: matches "race" in plan or event name

---

## Step 3 — Check Google Calendar

Use the Google Calendar connector to check yesterday's training event.
Note whether it existed and what it was.

---

## Step 4 — Create yesterday's day JSON

Write `data/weeks/{week-id}/{YYYY-MM-DD-day}.json` where `day` is the three-letter lowercase day name (mon, tue, wed, thu, fri, sat, sun).

```json
{
  "date": "YYYY-MM-DD",
  "day_of_week": "monday",
  "week_id": "YYYY-WXX",
  "planned": {
    "type": "run|gym|run+gym|rest",
    "description": "What was planned from week.json",
    "calendar_event_id": "from the calendar if available"
  },
  "completed": true,
  "activity": {
    "type": "run",
    "run_type": "easy|tempo|long|interval|race|recovery",
    "distance_km": 6.2,
    "pace_per_km": "6:45",
    "duration_minutes": 42,
    "heart_rate_avg": 142,
    "heart_rate_max": 158,
    "elevation_m": 35,
    "shoes": "Nike Pegasus 41",
    "strava_activity_id": "12345"
  },
  "gym": {
    "completed": true,
    "type": "legs|chest+triceps|back+biceps|shoulders+abs",
    "notes": ""
  },
  "daily_comment": {
    "summary": "2-3 sentence analysis of the day's training",
    "did_right": [
      "Specific positive observation with numbers",
      "Another positive point"
    ],
    "to_improve": [
      "Specific actionable improvement with numbers",
      "Another improvement area"
    ],
    "generated_at": "<ISO 8601 timestamp>"
  }
}
```

**Rules:**
- If no run was recorded but one was planned, set `completed` to `false` and `activity` to `null`
- If a run was recorded but none was planned, still log it with `completed: true`
- If the plan was gym-only and no Strava activity exists, set `activity` to `null` and `gym.completed` based on calendar event status
- For rest days with no activity, set `completed: true`, `activity: null`, `gym: null`
- Set `gym` to `null` if no gym was planned or done

---

## Step 5 — Generate the daily comment

Analyze yesterday's training. The comment should be:
- **Specific and data-driven** — reference actual pace, distance, HR numbers
- **Compared to plan** — did they do what was planned?
- **Contextual** — consider the training phase, race dates, and recent load
- **Actionable** — "to_improve" items should be concrete

For `did_right`: Things the athlete executed well. Be specific with numbers.
For `to_improve`: Things to work on. Be specific and actionable, not generic.

If no activity was recorded:
- `summary`: Note the missed session, assess whether rest was needed or it's a concern
- `did_right`: If rest was appropriate, say so
- `to_improve`: Suggest making up the session or adjusting the week plan

---

## Step 6 — Mark completion in Google Calendar

If the planned session was completed, update the Google Calendar event title to include ✅.
If it was missed, update to include ❌.

Example: `Treino: Easy run Zone 2 ✅` or `Treino: VO2max intervals ❌`

---

## Step 7 — Update the manifest

Read `data/manifest.json`. Add yesterday's day file to the current week's `days` array.
Update `updated_at`.

Write the updated `data/manifest.json`.

---

## Step 8 — Commit and push

```bash
git add data/
git commit -m "chore: daily sync $(date +%Y-%m-%d)"
git push origin main
```
