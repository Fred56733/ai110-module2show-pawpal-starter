# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python main.py`:

```
=== Today's Schedule ===
Daily plan for Jordan (2026-11-05):
  08:00 - Morning walk (Mochi) (30 min) [priority: high]
  08:30 - Breakfast (Luna) (10 min) [priority: high]
  08:40 - Play session (Luna) (15 min) [priority: medium]
  12:00 - Medication (Mochi) (5 min) [priority: high]

=== Why This Plan ===
Plan for 2026-11-05: 4 task(s) using 60 of 75 available minutes.
- 08:00 Morning walk (Mochi): High priority, at its preferred time
- 08:30 Breakfast (Luna): High priority, at its preferred time
- 08:40 Play session (Luna): Medium priority, in the next free slot
- 12:00 Medication (Mochi): High priority, at its preferred time
Skipped:
- Grooming (Luna): Needs 45 min but only 15 min left
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

PawPal+ goes beyond a simple task list with the features below. They live in `pawpal_system.py` and are demonstrated in `main.py`. The Streamlit app doesn't use them yet.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | `sort_by_time()` orders tasks by preferred time and puts untimed tasks last. `sort_tasks()` orders by highest priority, then shortest duration, to decide what gets planned first. |
| Filtering | `Owner.filter_tasks()`, `Scheduler.fit_tasks()` | `filter_tasks()` finds tasks by pet name, completion status, day or any mix of these. `fit_tasks()` skips tasks that don't fit the owner's available time and records why. |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.assign_times()` | `assign_times()` keeps preferred times and fits other tasks into free gaps. `detect_conflicts()` returns a warning for each overlap, for the same pet or different pets, without stopping the program. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()`, `Task.is_due()` | Completing a daily or weekly task automatically adds a new one, due 1 or 7 days after the day it was completed. Completing a task twice doesn't create a duplicate. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
