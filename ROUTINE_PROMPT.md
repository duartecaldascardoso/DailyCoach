# Training Dashboard — Routine Prompt

Paste this as the prompt when creating your Claude routine at claude.ai/code/routines.
Set the trigger to daily (e.g. 07:00 UTC). Include the Strava and Google Calendar connectors.

---

## Task

Update the training dashboard by fetching today's Strava and Google Calendar data, writing
three JSON files, and pushing them to the repo. The dashboard at index.html reads these files.

---

## Step 1 — Fetch Strava data

Use the Strava connector to retrieve:
- All runs/activities from the last 14 days
- For each activity: name, date, distance (km, 1 decimal), moving time (minutes), average pace
  (min/km as M:SS), total elevation gain (m), and sport type

Calculate week summary for the current Monday–Sunday week:
- total_distance_km (1 decimal)
- total_runs (integer count of running activities)
- total_elevation_m (integer)
- total_time_minutes (integer)

Classify each activity type as one of: easy | tempo | long | interval | race | recovery
Use pace and distance as signals: long = >14 km, interval = short with fast segments,
tempo = sustained effort near threshold, easy = conversational pace.

---

## Step 2 — Fetch Google Calendar data

Use the Google Calendar connector to retrieve all events for the next 7 days.
Filter to only include events that are training, workout, or race related.
Include at most 5 events.

---

## Step 3 — Write data/activities.json

```json
{
  "updated_at": "<ISO 8601 timestamp of now>",
  "week_summary": {
    "total_distance_km": 0.0,
    "total_runs": 0,
    "total_elevation_m": 0,
    "total_time_minutes": 0
  },
  "recent_activities": [
    {
      "date": "YYYY-MM-DD",
      "name": "Activity name from Strava",
      "distance_km": 0.0,
      "pace_per_km": "M:SS",
      "duration_minutes": 0,
      "elevation_m": 0,
      "type": "easy"
    }
  ]
}
```

Include up to 8 most recent activities, newest first.

---

## Step 4 — Write data/calendar.json

```json
{
  "updated_at": "<ISO 8601 timestamp>",
  "upcoming_events": [
    {
      "date": "YYYY-MM-DD",
      "title": "Event name",
      "time": "HH:MM"
    }
  ]
}
```

---

## Step 5 — Write data/coaching.json

Analyze the training data and write concise coaching notes.

Context:
- Athlete: Duarte, training for distance running
- Goal A: Half Marathon, Porto, 13 September 2026
- Goal B: Marathon, Porto, 8 November 2026
- Training philosophy: consistent aerobic base, progressive long runs, 1 quality session/week

Notes should be specific, data-driven, and actionable — not generic encouragement.
Reference actual numbers (km, pace, elevation) from this week's data.
Note the current training phase relative to race dates.

```json
{
  "updated_at": "<ISO 8601 timestamp>",
  "summary": "2–4 sentence overview of recent training.",
  "key_observations": [
    "Specific observation referencing a metric",
    "Another specific observation",
    "Third observation or flag if something needs attention"
  ],
  "focus_next_week": "1–2 sentences on the single most important focus for next week."
}
```

---

## Step 6 — Commit and push

Stage and commit the three files:
```
git add data/activities.json data/calendar.json data/coaching.json
git commit -m "chore: sync training data $(date +%Y-%m-%d)"
git push origin main
```
