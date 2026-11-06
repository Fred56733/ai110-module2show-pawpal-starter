"""Temporary testing ground: run the PawPal+ logic in the terminal."""

from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(heading: str, tasks: list[Task]) -> None:
    """Print a heading and one readable line per task."""
    print(f"\n=== {heading} ===")
    if not tasks:
        print("  None")
    for task in tasks:
        when = f"{task.preferred_time:%H:%M}" if task.preferred_time else "Any time"
        print(f"  {when:<8} - {task.title} ({task.pet_name})")


def main() -> None:
    today = date.today()
    owner = Owner("Jordan", available_minutes=75)

    mochi = Pet("Mochi", "dog", age=4)
    luna = Pet("Luna", "cat", age=2)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of order on purpose, to show the sorting working.
    mochi.add_task(Task("Medication", 5, "high", "meds", preferred_time=time(12, 0)))
    luna.add_task(Task("Play session", 15, "medium", "enrichment"))
    mochi.add_task(Task("Morning walk", 30, "high", "walk", preferred_time=time(8, 0)))
    grooming = Task("Grooming", 45, "low", "grooming", frequency="weekly")
    breakfast = Task("Breakfast", 10, "high", "feeding", preferred_time=time(8, 30))
    luna.add_task(grooming)
    luna.add_task(breakfast)

    # Two clashes on purpose: one for the same pet and one across different pets.
    mochi.add_task(Task("Ear drops", 5, "high", "meds", preferred_time=time(8, 0)))
    luna.add_task(Task("Flea treatment", 5, "high", "meds", preferred_time=time(12, 0)))

    scheduler = Scheduler(owner)
    scheduler.generate_plan(today)

    print("=== Today's Schedule ===")
    print(scheduler.display_plan())
    print()
    print("=== Conflict Warnings ===")
    for warning in scheduler.detect_conflicts() or ["None"]:
        print(f"  {warning}")
    print()
    print("=== Why This Plan ===")
    print(scheduler.explain_plan())

    all_tasks = owner.get_all_tasks()
    print_tasks("All Tasks (As Added, By Pet)", all_tasks)
    print_tasks("All Tasks (Sorted By Time)", scheduler.sort_by_time(all_tasks))

    print_tasks("Luna's Tasks", owner.filter_tasks(pet_name="Luna"))

    print("\n=== Recurring Tasks ===")
    for task in (breakfast, grooming):
        next_task = scheduler.mark_task_complete(task, today)
        print(f"  {task.title} ({task.frequency}) is done, next due {next_task.due_date}")

    print_tasks("Completed Today", owner.filter_tasks(completed=True, day=today))
    print_tasks("Still To Do", owner.filter_tasks(completed=False, day=today))

    mochi_to_do = owner.filter_tasks(pet_name="Mochi", completed=False, day=today)
    print_tasks("Mochi Still To Do (Sorted By Time)", scheduler.sort_by_time(mochi_to_do))

    tomorrow = today + timedelta(days=1)
    print_tasks("Due Tomorrow", owner.filter_tasks(completed=False, day=tomorrow))


if __name__ == "__main__":
    main()
