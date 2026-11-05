"""Temporary testing ground: run the PawPal+ logic in the terminal."""

from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan", available_minutes=75)

    mochi = Pet("Mochi", "dog", age=4)
    luna = Pet("Luna", "cat", age=2)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Medication", 5, "high", "meds", preferred_time=time(12, 0)))
    mochi.add_task(Task("Morning walk", 30, "high", "walk", preferred_time=time(8, 0)))
    luna.add_task(Task("Breakfast", 10, "high", "feeding", preferred_time=time(8, 30)))
    luna.add_task(Task("Play session", 15, "medium", "enrichment"))
    luna.add_task(Task("Grooming", 45, "low", "grooming", frequency="weekly"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan(date.today())

    print("=== Today's Schedule ===")
    print(scheduler.display_plan())
    print()
    print("=== Why This Plan ===")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
