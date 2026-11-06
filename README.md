# 🐾 PawPal+

PawPal+ is a Streamlit app that helps busy pet owners stay consistent with pet care. You add your pets and their care tasks, and it builds a plan for the day based on your available time and each task's priority. It also explains its choices, warns you about time conflicts and keeps track of recurring tasks.

## ✨ Features

- **Multiple pets:** Keep tasks for all of your pets in one place, and see which pet each task belongs to.
- **Editable tasks:** Change a task's details or remove it at any time.
- **Priority-based planning:** Tasks are considered from highest to lowest priority, with shorter tasks first within each priority level.
- **Time budget:** The plan stays within your available minutes. Tasks that don't fit are skipped with a reason, and shorter tasks can still use the time that's left.
- **Sorting by time:** Tasks are listed by preferred time, earliest first, with untimed tasks last.
- **Preferred times and free slots:** Tasks with a preferred time keep it, and other tasks are placed in the earliest free gap.
- **Filtering:** Find tasks by pet, by completion status or by both.
- **Daily and weekly recurrence:** Completing a recurring task automatically creates the next one, due 1 or 7 days later.
- **Conflict warnings:** Overlapping tasks are flagged with a warning, whether they're for the same pet or different pets. The app keeps running and the plan stays visible.
- **Plan explanations:** Each planned task shows why it was placed there, and each skipped task shows why it was left out.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If your system doesn't have a `python` command, use `python3` for the first line.

### Run the app

```bash
streamlit run app.py
```

### Run the terminal demo

```bash
python main.py
```

### Project files

| File | Purpose |
|------|---------|
| `app.py` | The Streamlit app |
| `pawpal_system.py` | The `Owner`, `Pet`, `Task` and `Scheduler` classes |
| `main.py` | A terminal demo of the scheduling logic |
| `tests/test_pawpal.py` | The automated test suite |
| `diagrams/uml_final.mmd` | The final UML class diagram |

## 🖥️ Sample Output

The start of the output from running `python main.py`. The [Demo Walkthrough](#-demo-walkthrough) has the full output.

```
=== Today's Schedule ===
Daily plan for Jordan (2026-11-06):
  08:00 - Ear drops (Mochi) (5 min) [priority: high]
  08:00 - Morning walk (Mochi) (30 min) [priority: high]
  08:30 - Breakfast (Luna) (10 min) [priority: high]
  08:40 - Play session (Luna) (15 min) [priority: medium]
  12:00 - Medication (Mochi) (5 min) [priority: high]
  12:00 - Flea treatment (Luna) (5 min) [priority: high]

=== Conflict Warnings ===
  Warning: Ear drops (Mochi) and Morning walk (Mochi) both start at 08:00 [same pet]
  Warning: Medication (Mochi) and Flea treatment (Luna) both start at 12:00 [different pets]
```

## 🧪 Testing PawPal+

Run the full test suite from the project folder:

```bash
python -m pytest
```

If your system doesn't have a `python` command, use `python3 -m pytest`.

### What the tests cover

The 42 tests in `tests/test_pawpal.py` cover normal use and edge cases:

| Area | Tests | What they check |
|------|-------|-----------------|
| Basics | 2 | Completing a task changes its status, and adding a task increases a pet's task count |
| Sorting | 6 | Chronological order, untimed tasks last, midnight, same-time ties, an empty list, and priority order |
| Building a plan | 9 | Priority when time runs out, a pet with no tasks, an owner with no pets, an exact fit, zero available time, repeat runs, and tasks that would run past midnight |
| Filtering | 6 | By pet, by completion status, by both, an unknown pet, and upcoming tasks not counting as completed |
| Recurring tasks | 10 | Daily and weekly next dates, copied details, no duplicates, year ends, leap days, and late or early completion |
| Conflict detection | 9 | Same-time and overlapping tasks for one pet or two, back-to-back tasks, three tasks at once, and skipped tasks |

### Test output

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/fred/Documents/VS Code/ai110-module2show-pawpal-starter
collected 42 items

tests/test_pawpal.py ..........................................          [100%]

============================== 42 passed in 0.03s ==============================
```

### Confidence level

⭐⭐⭐⭐☆ (4/5)

All 42 tests pass, and they found three real bugs in the scheduling logic that were then fixed. The rating stops at 4 because the tests only cover `pawpal_system.py`, so the Streamlit app has no automated tests of its own.

## 📐 Smarter Scheduling

PawPal+ goes beyond a simple task list with the features below. They live in `pawpal_system.py` and are demonstrated in `main.py`. The Streamlit app uses them too, so you can sort and filter tasks, mark them complete and see conflict warnings in the browser.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | `sort_by_time()` orders tasks by preferred time and puts untimed tasks last. `sort_tasks()` orders by highest priority, then shortest duration, to decide what gets planned first. |
| Filtering | `Owner.filter_tasks()`, `Scheduler.fit_tasks()` | `filter_tasks()` finds tasks by pet name, completion status, day or any mix of these. `fit_tasks()` skips tasks that don't fit the owner's available time and records why. |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.assign_times()` | `assign_times()` keeps preferred times and fits other tasks into free gaps. `detect_conflicts()` returns a warning for each overlap, for the same pet or different pets, without stopping the program. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()`, `Task.is_due()` | Completing a daily or weekly task automatically adds a new one, due 1 or 7 days after the day it was completed, or after its due date if it was completed early. Completing a task twice doesn't create a duplicate. |

## 📸 Demo Walkthrough

### Main UI features

| Section | What you can do |
|---------|-----------------|
| **Owner** | Enter your name and the minutes you have available today |
| **Pets** | Add a pet with a name and species. Blank and duplicate names are rejected |
| **Tasks** | Add a task for a pet with a title, duration, priority, frequency and optional preferred time |
| **Task due today** | Choose a task and click **Mark complete** |
| **Edit or remove a task** | Change an unfinished task's title, duration, priority, frequency or preferred time, or remove it |
| **Show pet and Show status** | Filter the task table by pet and by Due today, Completed or All |
| **Build Schedule** | Click **Generate schedule** to see today's plan, any conflicts and any skipped tasks |

### Example workflow

This example enters the same pets and tasks as `main.py`.

1. **Set your time.** Under **Owner**, set **Minutes available today** to 75.
2. **Add your pets.** Add Mochi (dog) and Luna (cat). They appear in the pets table.
3. **Add tasks.** Add the tasks below, in any order. The task table sorts them by preferred time as you go.

   | Pet | Task | Minutes | Priority | Frequency | Preferred time |
   |-----|------|---------|----------|-----------|----------------|
   | Mochi | Medication | 5 | high | daily | 12:00 |
   | Mochi | Morning walk | 30 | high | daily | 08:00 |
   | Mochi | Ear drops | 5 | high | daily | 08:00 |
   | Luna | Play session | 15 | medium | daily | None |
   | Luna | Grooming | 45 | low | weekly | None |
   | Luna | Breakfast | 10 | high | daily | 08:30 |
   | Luna | Flea treatment | 5 | high | daily | 12:00 |

4. **Filter the list.** Set **Show pet** to Luna to see only Luna's tasks, then set it back to All pets.
5. **Generate the plan.** Click **Generate schedule**. A green message reports 6 tasks using 70 of 75 available minutes.
6. **Review the conflicts.** A yellow box lists 2 time conflicts, one for Mochi at 08:00 and one between the two pets at 12:00.
7. **Read the plan.** The plan table shows each task's start time and why it's there. Grooming appears under **Skipped tasks** because it needs 45 minutes and only 5 are left.
8. **Complete a task.** Choose Breakfast (Luna) and click **Mark complete**. A message shows it's next due tomorrow.
9. **Check the result.** Set **Show status** to All to see the finished Breakfast and the new one. Click **Generate schedule** again, and Breakfast is no longer in today's plan.
10. **Fix a conflict.** Open **Edit or remove a task**, choose Ear drops (Mochi), change its preferred time to 09:00 and click **Save changes**. Click **Generate schedule** again, and only the 12:00 conflict remains.
11. **Remove a task.** Choose Flea treatment (Luna) and click **Remove task**. Click **Generate schedule** again, and the conflict warning is gone.

### Key Scheduler behaviors shown

| Behavior | Where you can see it |
|----------|----------------------|
| **Sorting by time** | Tasks added out of order appear earliest first, with untimed tasks last |
| **Choosing by priority** | High-priority tasks are planned first, and low-priority Grooming is the one left out |
| **Time budget** | The plan uses 70 of 75 minutes and gives a reason for skipping Grooming |
| **Filling free slots** | Play session has no preferred time, so it goes in the first free gap at 08:40 |
| **Conflict warnings** | Same-time tasks are flagged for one pet and across two pets, and both stay in the plan |
| **Recurrence** | Completing a daily task creates one for tomorrow, and a weekly task creates one for 7 days later |
| **Filtering** | Tasks can be narrowed by pet, by status or by both |

### Sample CLI output

The full output from running `python main.py`:

```
=== Today's Schedule ===
Daily plan for Jordan (2026-11-06):
  08:00 - Ear drops (Mochi) (5 min) [priority: high]
  08:00 - Morning walk (Mochi) (30 min) [priority: high]
  08:30 - Breakfast (Luna) (10 min) [priority: high]
  08:40 - Play session (Luna) (15 min) [priority: medium]
  12:00 - Medication (Mochi) (5 min) [priority: high]
  12:00 - Flea treatment (Luna) (5 min) [priority: high]

=== Conflict Warnings ===
  Warning: Ear drops (Mochi) and Morning walk (Mochi) both start at 08:00 [same pet]
  Warning: Medication (Mochi) and Flea treatment (Luna) both start at 12:00 [different pets]

=== Why This Plan ===
Plan for 2026-11-06: 6 task(s) using 70 of 75 available minutes.
- 08:00 Ear drops (Mochi): High priority, at its preferred time
- 08:00 Morning walk (Mochi): High priority, at its preferred time
- 08:30 Breakfast (Luna): High priority, at its preferred time
- 08:40 Play session (Luna): Medium priority, in the next free slot
- 12:00 Medication (Mochi): High priority, at its preferred time
- 12:00 Flea treatment (Luna): High priority, at its preferred time
Skipped:
- Grooming (Luna): Needs 45 min but only 5 min left
Conflicts:
- Warning: Ear drops (Mochi) and Morning walk (Mochi) both start at 08:00 [same pet]
- Warning: Medication (Mochi) and Flea treatment (Luna) both start at 12:00 [different pets]

=== All Tasks (As Added, By Pet) ===
  12:00    - Medication (Mochi)
  08:00    - Morning walk (Mochi)
  08:00    - Ear drops (Mochi)
  Any time - Play session (Luna)
  Any time - Grooming (Luna)
  08:30    - Breakfast (Luna)
  12:00    - Flea treatment (Luna)

=== All Tasks (Sorted By Time) ===
  08:00    - Morning walk (Mochi)
  08:00    - Ear drops (Mochi)
  08:30    - Breakfast (Luna)
  12:00    - Medication (Mochi)
  12:00    - Flea treatment (Luna)
  Any time - Play session (Luna)
  Any time - Grooming (Luna)

=== Luna's Tasks ===
  Any time - Play session (Luna)
  Any time - Grooming (Luna)
  08:30    - Breakfast (Luna)
  12:00    - Flea treatment (Luna)

=== Recurring Tasks ===
  Breakfast (daily) is done, next due 2026-11-07
  Grooming (weekly) is done, next due 2026-11-13

=== Completed Today ===
  Any time - Grooming (Luna)
  08:30    - Breakfast (Luna)

=== Still To Do ===
  12:00    - Medication (Mochi)
  08:00    - Morning walk (Mochi)
  08:00    - Ear drops (Mochi)
  Any time - Play session (Luna)
  12:00    - Flea treatment (Luna)

=== Mochi Still To Do (Sorted By Time) ===
  08:00    - Morning walk (Mochi)
  08:00    - Ear drops (Mochi)
  12:00    - Medication (Mochi)

=== Due Tomorrow ===
  12:00    - Medication (Mochi)
  08:00    - Morning walk (Mochi)
  08:00    - Ear drops (Mochi)
  Any time - Play session (Luna)
  12:00    - Flea treatment (Luna)
  08:30    - Breakfast (Luna)
```

## ⚠️ Known limitations

- Conflicts are flagged but not resolved automatically. The owner decides which task should move.
- A task can't be moved to a different pet. Remove it and add it again instead.
- Data lasts only for the current browser session, so refreshing the page clears it.
- The day always starts at 08:00 in the app, so a task with an earlier preferred time moves to 08:00.
- Owner preferences can be stored on `Owner`, but the scheduler doesn't use them yet.
