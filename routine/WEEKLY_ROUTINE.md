# Weekly Training Routine — Sunday 6pm

Paste this as the prompt when creating your Claude routine at claude.ai/code/routines.
Set the trigger to **every Sunday at 18:00 (local time)**. Include the **Strava** and **Google Calendar** connectors (with write access).

---

## Context

- **Athlete**: Duarte Cardoso, training for distance running
- **Goal A**: Half Marathon, Porto, 13 September 2026
- **Goal B**: Marathon, Porto, 8 November 2026
- **Training philosophy**: Consistent aerobic base, progressive long runs, 1 quality session/week, integrated gym work
- **Repo**: This GitHub Pages repo at `data/weeks/` stores all training data
- **Week format**: ISO weeks (Monday–Sunday), folder named `YYYY-WXX`

---

## Step 1 — Review the past week

Read all day JSON files from the current week's folder (`data/weeks/{current-week-id}/`).
Also read the `week.json` file's `plan` section.

For each day that has a JSON file, check:
- Was the planned session completed?
- What were the key metrics (distance, pace, HR, etc.)?

Calculate:
- `completion_rate` — ratio of completed sessions to planned sessions (0.0 to 1.0)
- `total_km` — sum of all run distances
- `total_runs` — count of run activities
- `total_gym_sessions` — count of gym completions
- `total_time_minutes` — sum of all run durations
- `avg_pace` — weighted average pace across all runs

Write the `review` section of this week's `week.json`:

```json
{
  "review": {
    "summary": "2-4 sentence overview of the week, referencing specific numbers",
    "completion_rate": 0.85,
    "total_km": 32.0,
    "total_runs": 4,
    "total_gym_sessions": 3,
    "total_time_minutes": 220,
    "avg_pace": "6:10",
    "highlights": ["Specific achievement 1", "Specific achievement 2"],
    "areas_to_improve": ["Specific improvement 1", "Specific improvement 2"]
  },
  "reviewed_at": "<ISO 8601 timestamp>"
}
```

Be specific and data-driven. Reference actual numbers. Note the training phase relative to race dates.

---

## Step 2 — Plan next week

Calculate the next week's ISO week ID (e.g., if current is W25, next is W26).
Create the folder `data/weeks/{next-week-id}/`.

Based on:
- The review of this week (progression, fatigue, completion)
- Current training phase relative to race dates
- Training philosophy (progressive overload, recovery weeks every 3-4 weeks)

Plan the next week's sessions. Include a mix of:
- **Easy runs** (Zone 2, conversational pace 6:30-7:30/km)
- **Quality session** (tempo, intervals, or VO2max — 1 per week)
- **Long run** (Sunday, progressive — increase by 1-2 km per week, cap at 22 km for HM prep)
- **Gym sessions** (rotate: Legs, Chest+Triceps, Back+Biceps, Shoulders+Abs)
- **Rest days** (at least 1, ideally Saturday before long run Sunday)

Write `data/weeks/{next-week-id}/week.json`:

```json
{
  "week_id": "YYYY-WXX",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "plan": {
    "summary": "2-3 sentence overview of what this week focuses on",
    "sessions": [
      {
        "day": "monday",
        "type": "run|gym|run+gym|rest",
        "description": "Detailed description of the session"
      }
    ]
  },
  "review": null,
  "created_at": "<ISO 8601 timestamp>",
  "reviewed_at": null
}
```

---

## Step 3 — Create Google Calendar events

For each session in the next week's plan, create a Google Calendar event:
- **Title**: `Treino: {description}`
- **Date**: The corresponding day of the next week
- **All-day event** (no specific time)
- **Calendar**: Use the default calendar

Store the `calendar_event_id` from Google Calendar in each session object.

---

## Step 4 — Update the manifest

Read `data/manifest.json`. Add the new week entry (with empty `days` array since no day files exist yet).
Update `reviewed_at` for the current week. Update the `updated_at` timestamp.

Write the updated `data/manifest.json`.

---

## Step 5 — Commit and push

```bash
git add data/
git commit -m "chore: weekly review & plan $(date +%Y-%m-%d)"
git push origin main
```
