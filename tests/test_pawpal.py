from datetime import date, time

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

DAY = date(2026, 11, 6)
NEXT_DAY = date(2026, 11, 7)


def make_scheduler(*tasks, minutes=120, day_start=time(8, 0)):
    """Return a Scheduler for an owner with one pet, Mochi, holding the given tasks."""
    owner = Owner("Jordan", minutes, day_start=day_start)
    owner.add_pet(Pet("Mochi", "dog"))
    for task in tasks:
        owner.pets[0].add_task(task)
    return Scheduler(owner)


def make_two_pet_owner():
    """Return an owner with Mochi and Luna, where Luna's Breakfast is already done."""
    owner = Owner("Jordan", 120)
    mochi = Pet("Mochi", "dog", tasks=[Task("Walk", 30)])
    luna = Pet("Luna", "cat", tasks=[Task("Play", 15), Task("Breakfast", 10)])
    owner.add_pet(mochi)
    owner.add_pet(luna)
    Scheduler(owner).mark_task_complete(luna.tasks[1], DAY)
    return owner


def timed_task(title, hour, minute=0, duration=30):
    """Return a task with a preferred time."""
    return Task(title, duration, preferred_time=time(hour, minute))


def titles(tasks):
    """Return the titles of the given tasks."""
    return [task.title for task in tasks]


def planned_titles(scheduler):
    """Return the titles of the scheduler's planned tasks."""
    return [item["task"].title for item in scheduler.planned_items]


def skipped_titles(scheduler):
    """Return the titles of the scheduler's skipped tasks."""
    return [item["task"].title for item in scheduler.skipped_items]


# Basics


def test_mark_complete_changes_task_status():
    day = date(2026, 11, 5)
    task = Task("Morning walk", 30)
    assert task.last_completed is None
    assert task.is_due(day)

    task.mark_complete(day)

    assert task.last_completed == day
    assert not task.is_due(day)


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Morning walk", 30))

    assert len(pet.tasks) == 1


# Sorting


def test_sort_by_time_returns_chronological_order():
    tasks = [timed_task("Noon", 12), timed_task("Early", 7), timed_task("Mid", 9, 30)]

    result = make_scheduler().sort_by_time(tasks)

    assert titles(result) == ["Early", "Mid", "Noon"]


def test_sort_by_time_puts_untimed_tasks_last():
    tasks = [Task("Any time", 10), timed_task("Timed", 18)]

    result = make_scheduler().sort_by_time(tasks)

    assert titles(result) == ["Timed", "Any time"]


def test_sort_by_time_puts_midnight_first():
    tasks = [timed_task("Morning", 8), timed_task("Midnight", 0)]

    result = make_scheduler().sort_by_time(tasks)

    assert titles(result) == ["Midnight", "Morning"]


def test_sort_by_time_keeps_order_of_tasks_at_the_same_time():
    tasks = [timed_task("First added", 9), timed_task("Second added", 9)]

    result = make_scheduler().sort_by_time(tasks)

    assert titles(result) == ["First added", "Second added"]


def test_sort_by_time_handles_an_empty_list():
    assert make_scheduler().sort_by_time([]) == []


def test_sort_tasks_orders_by_priority_then_shortest():
    tasks = [
        Task("Low", 5, "low"),
        Task("Long high", 30, "high"),
        Task("Short high", 10, "high"),
        Task("Medium", 5, "medium"),
    ]

    result = make_scheduler().sort_tasks(tasks)

    assert titles(result) == ["Short high", "Long high", "Medium", "Low"]


# Building a plan


def test_plan_chooses_high_priority_tasks_when_time_runs_out():
    scheduler = make_scheduler(
        Task("Grooming", 45, "low"), Task("Walk", 30, "high"), minutes=40
    )

    scheduler.generate_plan(DAY)

    assert planned_titles(scheduler) == ["Walk"]
    assert skipped_titles(scheduler) == ["Grooming"]
    assert scheduler.skipped_items[0]["reason"] == "Needs 45 min but only 10 min left"


def test_plan_is_empty_for_a_pet_with_no_tasks():
    assert make_scheduler().generate_plan(DAY) == []


def test_plan_is_empty_for_an_owner_with_no_pets():
    assert Scheduler(Owner("Jordan", 60)).generate_plan(DAY) == []


def test_task_that_exactly_fills_the_time_is_planned():
    scheduler = make_scheduler(Task("Walk", 30), minutes=30)

    scheduler.generate_plan(DAY)

    assert planned_titles(scheduler) == ["Walk"]


def test_zero_available_minutes_skips_every_task():
    scheduler = make_scheduler(Task("Walk", 5), minutes=0)

    scheduler.generate_plan(DAY)

    assert planned_titles(scheduler) == []
    assert skipped_titles(scheduler) == ["Walk"]


def test_generating_twice_does_not_duplicate_the_plan():
    scheduler = make_scheduler(Task("Walk", 30), Task("Grooming", 200))

    scheduler.generate_plan(DAY)
    scheduler.generate_plan(DAY)

    assert planned_titles(scheduler) == ["Walk"]
    assert skipped_titles(scheduler) == ["Grooming"]


def test_preferred_time_before_the_day_starts_moves_to_the_day_start():
    scheduler = make_scheduler(timed_task("Meds", 6), day_start=time(8, 0))

    scheduler.generate_plan(DAY)

    assert scheduler.planned_items[0]["start_time"] == time(8, 0)


def test_task_past_midnight_does_not_use_up_the_available_time():
    late = Task("Late", 50, "high", preferred_time=time(23, 50))
    scheduler = make_scheduler(late, Task("Short", 20, "low"), minutes=60)

    scheduler.generate_plan(DAY)

    assert planned_titles(scheduler) == ["Short"]
    assert skipped_titles(scheduler) == ["Late"]
    assert scheduler.skipped_items[0]["reason"] == "Would run past midnight"


def test_completed_task_leaves_the_plan_after_regenerating():
    task = Task("Walk", 30)
    scheduler = make_scheduler(task)
    scheduler.generate_plan(DAY)

    scheduler.mark_task_complete(task, DAY)

    assert planned_titles(scheduler) == ["Walk"]  # unchanged until regenerated
    assert scheduler.generate_plan(DAY) == []


# Filtering


def test_filter_by_pet_name():
    owner = make_two_pet_owner()

    assert titles(owner.filter_tasks(pet_name="Mochi")) == ["Walk"]


def test_filter_by_completed_status():
    owner = make_two_pet_owner()

    assert titles(owner.filter_tasks(completed=True)) == ["Breakfast"]


def test_filter_by_pet_and_status_together():
    owner = make_two_pet_owner()

    result = owner.filter_tasks(pet_name="Luna", completed=False, day=DAY)

    assert titles(result) == ["Play"]


def test_filter_by_unknown_pet_returns_nothing():
    assert make_two_pet_owner().filter_tasks(pet_name="Nobody") == []


def test_filter_with_no_filters_returns_every_task():
    owner = make_two_pet_owner()

    assert owner.filter_tasks() == owner.get_all_tasks()


def test_next_occurrence_is_not_counted_as_completed_or_due_today():
    owner = make_two_pet_owner()

    assert "Breakfast" not in titles(owner.filter_tasks(completed=False, day=DAY))
    assert "Breakfast" in titles(owner.filter_tasks(completed=False, day=NEXT_DAY))


# Recurring tasks


def test_completing_a_daily_task_creates_a_task_for_the_next_day():
    task = Task("Walk", 30)
    scheduler = make_scheduler(task)

    next_task = scheduler.mark_task_complete(task, DAY)

    assert next_task is not task
    assert next_task.due_date == NEXT_DAY
    assert not next_task.is_complete()
    assert len(scheduler.owner.pets[0].tasks) == 2


def test_completing_a_weekly_task_creates_a_task_seven_days_later():
    task = Task("Bath", 20, frequency="weekly")
    scheduler = make_scheduler(task)

    next_task = scheduler.mark_task_complete(task, DAY)

    assert next_task.due_date == date(2026, 11, 13)


def test_next_occurrence_keeps_the_task_details():
    task = Task("Walk", 30, "high", "walk", preferred_time=time(8, 0))
    scheduler = make_scheduler(task)

    next_task = scheduler.mark_task_complete(task, DAY)

    assert next_task.title == "Walk"
    assert next_task.duration_minutes == 30
    assert next_task.priority == "high"
    assert next_task.category == "walk"
    assert next_task.frequency == "daily"
    assert next_task.preferred_time == time(8, 0)
    assert next_task.pet_name == "Mochi"


def test_completing_a_task_twice_does_not_create_a_duplicate():
    task = Task("Walk", 30)
    scheduler = make_scheduler(task)

    scheduler.mark_task_complete(task, DAY)
    result = scheduler.mark_task_complete(task, DAY)

    assert result is None
    assert len(scheduler.owner.pets[0].tasks) == 2


def test_next_due_date_crosses_the_end_of_the_year():
    next_task = Task("Walk", 30).next_occurrence(date(2026, 12, 31))

    assert next_task.due_date == date(2027, 1, 1)


def test_next_due_date_lands_on_a_leap_day():
    next_task = Task("Walk", 30).next_occurrence(date(2028, 2, 28))

    assert next_task.due_date == date(2028, 2, 29)


def test_late_completion_counts_from_the_completion_day():
    task = Task("Walk", 30, due_date=date(2026, 11, 1))
    scheduler = make_scheduler(task)

    next_task = scheduler.mark_task_complete(task, DAY)

    assert next_task.due_date == NEXT_DAY


def test_early_completion_counts_from_the_due_date():
    task = Task("Walk", 30, due_date=NEXT_DAY)
    scheduler = make_scheduler(task)

    next_task = scheduler.mark_task_complete(task, DAY)

    assert next_task.due_date == date(2026, 11, 8)


def test_completing_a_task_from_outside_the_owners_pets_raises_an_error():
    stray = Task("Stray", 5)

    with pytest.raises(ValueError):
        make_scheduler().mark_task_complete(stray, DAY)

    assert not stray.is_complete()


def test_next_occurrence_goes_to_the_right_pet_when_pets_share_a_name():
    owner = Owner("Jordan", 60)
    first_pet = Pet("Max", "dog", tasks=[Task("Feed", 5)])
    second_pet = Pet("Max", "cat", tasks=[Task("Feed", 5)])
    owner.add_pet(first_pet)
    owner.add_pet(second_pet)

    Scheduler(owner).mark_task_complete(second_pet.tasks[0], DAY)

    assert len(first_pet.tasks) == 1
    assert len(second_pet.tasks) == 2


# Conflict detection


def test_same_time_for_the_same_pet_is_flagged():
    scheduler = make_scheduler(timed_task("Walk", 9), timed_task("Ear drops", 9))

    scheduler.generate_plan(DAY)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "both start at 09:00" in warnings[0]
    assert "[same pet]" in warnings[0]


def test_same_time_for_different_pets_is_flagged():
    owner = Owner("Jordan", 120)
    owner.add_pet(Pet("Mochi", "dog", tasks=[timed_task("Walk", 9)]))
    owner.add_pet(Pet("Luna", "cat", tasks=[timed_task("Breakfast", 9)]))
    scheduler = Scheduler(owner)

    scheduler.generate_plan(DAY)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "[different pets]" in warnings[0]


def test_partial_overlap_is_flagged():
    scheduler = make_scheduler(timed_task("Walk", 9), timed_task("Feed", 9, 29))

    scheduler.generate_plan(DAY)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "overlap (09:00 and 09:29)" in warnings[0]


def test_back_to_back_tasks_are_not_a_conflict():
    scheduler = make_scheduler(timed_task("Walk", 9), timed_task("Feed", 9, 30))

    scheduler.generate_plan(DAY)

    assert scheduler.detect_conflicts() == []


def test_three_tasks_at_the_same_time_give_a_warning_per_pair():
    scheduler = make_scheduler(
        timed_task("A", 9), timed_task("B", 9), timed_task("C", 9)
    )

    scheduler.generate_plan(DAY)

    assert len(scheduler.detect_conflicts()) == 3


def test_skipped_task_does_not_cause_a_conflict():
    scheduler = make_scheduler(timed_task("A", 9), timed_task("B", 9), minutes=30)

    scheduler.generate_plan(DAY)

    assert scheduler.detect_conflicts() == []


def test_conflicting_tasks_both_stay_in_the_plan():
    scheduler = make_scheduler(timed_task("A", 9), timed_task("B", 9))

    scheduler.generate_plan(DAY)

    assert planned_titles(scheduler) == ["A", "B"]


def test_task_without_a_preferred_time_avoids_a_conflict():
    scheduler = make_scheduler(timed_task("Walk", 8), Task("Feed", 10))

    scheduler.generate_plan(DAY)

    assert scheduler.detect_conflicts() == []
    assert scheduler.planned_items[1]["start_time"] == time(8, 30)


def test_no_conflicts_before_a_plan_is_generated():
    assert make_scheduler().detect_conflicts() == []
