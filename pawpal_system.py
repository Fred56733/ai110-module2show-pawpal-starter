"""PawPal+ logic layer: the backend classes for planning pet care tasks."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta

PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}
FREQUENCY_DAYS = {"daily": 1, "weekly": 7}
MINUTES_PER_DAY = 24 * 60


def _to_minutes(clock_time: time) -> int:
    """Convert a time to minutes since midnight."""
    return clock_time.hour * 60 + clock_time.minute


def _to_time(minutes: int) -> time:
    """Convert minutes since midnight to a time."""
    return time(minutes // 60, minutes % 60)


@dataclass
class Task:
    """A single pet care activity, such as a walk or a feeding."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium" or "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds"
    frequency: str = "daily"  # "daily" or "weekly"
    preferred_time: time | None = None
    last_completed: date | None = None
    pet_name: str = ""  # set by the Pet that holds this task
    due_date: date | None = None  # None means it's due straight away

    def __post_init__(self) -> None:
        """Reject values the scheduler can't work with."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        if self.priority not in PRIORITY_RANKS:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANKS)}")
        if self.frequency not in FREQUENCY_DAYS:
            raise ValueError(f"frequency must be one of {list(FREQUENCY_DAYS)}")

    def update(self, details: dict) -> None:
        """Change this task's attributes using the given field names and values.

        Nothing changes if any field name or value is invalid.
        """
        replace(self, **details)  # raises before this task is touched
        for name, value in details.items():
            setattr(self, name, value)

    def mark_complete(self, day: date) -> None:
        """Record that this task was completed on the given day."""
        self.last_completed = day

    def is_due(self, day: date) -> bool:
        """Return True if this task is unfinished and has reached its due date."""
        if self.is_complete():
            return False
        return self.due_date is None or day >= self.due_date

    def is_complete(self) -> bool:
        """Return True if this occurrence of the task has been completed."""
        return self.last_completed is not None

    def next_occurrence(self, day: date) -> Task:
        """Return a new unfinished copy of this task, due one interval after the day."""
        interval = timedelta(days=FREQUENCY_DAYS[self.frequency])
        return replace(self, due_date=day + interval, last_completed=None)

    def priority_rank(self) -> int:
        """Return this task's priority as a number, where higher is more important."""
        return PRIORITY_RANKS[self.priority]


@dataclass
class Pet:
    """An animal and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Link any tasks passed in at creation to this pet."""
        for task in self.tasks:
            task.pet_name = self.name

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        self.tasks.remove(task)

    def get_tasks_due(self, day: date) -> list[Task]:
        """Return this pet's tasks that are due on the given day."""
        return [task for task in self.tasks if task.is_due(day)]


@dataclass
class Owner:
    """A pet owner, their pets and their daily constraints."""

    name: str
    available_minutes: int
    day_start: time = time(8, 0)
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return the tasks for all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_tasks_due(self, day: date) -> list[Task]:
        """Return the tasks due on the given day across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks_due(day)]

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        day: date | None = None,
    ) -> list[Task]:
        """Return the tasks matching the given pet name, status and day.

        A task matches a day if it was completed or is due on that day. Leave a
        filter as None to ignore it.
        """
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [task for task in tasks if task.pet_name == pet_name]
        if completed is not None:
            tasks = [task for task in tasks if task.is_complete() == completed]
        if day is not None:
            tasks = [
                task for task in tasks if task.last_completed == day or task.is_due(day)
            ]
        return tasks


@dataclass
class Scheduler:
    """Builds a daily plan for an owner and explains its choices."""

    owner: Owner
    plan_date: date | None = None
    planned_items: list[dict] = field(default_factory=list)  # task, start_time, reason
    skipped_items: list[dict] = field(default_factory=list)  # task, reason

    def generate_plan(self, day: date) -> list[dict]:
        """Build and return the plan for the given day, replacing any earlier plan."""
        self.plan_date = day
        ordered_tasks = self.sort_tasks(self.owner.get_tasks_due(day))
        fitting_tasks, skipped_for_time = self.fit_tasks(ordered_tasks)
        self.planned_items, skipped_for_day_end = self.assign_times(fitting_tasks)
        self.skipped_items = skipped_for_time + skipped_for_day_end
        return self.planned_items

    def mark_task_complete(self, task: Task, day: date) -> Task | None:
        """Complete the task and add its next occurrence to the same pet.

        Returns the new task, or None if this task was already complete, so that
        completing it twice can't create a duplicate.
        """
        pet = next((pet for pet in self.owner.pets if task in pet.tasks), None)
        if pet is None:
            raise ValueError(f"{task.title} doesn't belong to any of this owner's pets")
        if task.is_complete():
            return None
        task.mark_complete(day)
        next_task = task.next_occurrence(day)
        pet.add_task(next_task)
        return next_task

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks by highest priority first, then shortest first."""
        return sorted(
            tasks, key=lambda task: (-task.priority_rank(), task.duration_minutes)
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks by preferred time, earliest first, with untimed tasks last."""
        return sorted(
            tasks,
            key=lambda task: (
                task.preferred_time is None,
                task.preferred_time or time.max,
            ),
        )

    def fit_tasks(self, tasks: list[Task]) -> tuple[list[Task], list[dict]]:
        """Split the tasks into those that fit the owner's time and those that don't.

        Tasks are considered in the order given. A task that doesn't fit is skipped
        and the next one is still tried, so a shorter task can use the time left.
        """
        minutes_left = self.owner.available_minutes
        fitting_tasks = []
        skipped_items = []
        for task in tasks:
            if task.duration_minutes <= minutes_left:
                fitting_tasks.append(task)
                minutes_left -= task.duration_minutes
            else:
                reason = (
                    f"Needs {task.duration_minutes} min "
                    f"but only {minutes_left} min left"
                )
                skipped_items.append({"task": task, "reason": reason})
        return fitting_tasks, skipped_items

    def assign_times(self, tasks: list[Task]) -> tuple[list[dict], list[dict]]:
        """Give each task a start time, returning planned items and skipped items.

        Tasks with a preferred time keep it, even if that causes an overlap, so that
        detect_conflicts can warn the owner. Other tasks fill the earliest free gap.
        A task that would run past midnight is skipped.
        """
        day_start = _to_minutes(self.owner.day_start)
        with_preference = [task for task in tasks if task.preferred_time is not None]
        without_preference = [task for task in tasks if task.preferred_time is None]
        busy_periods = []
        planned_items = []
        skipped_items = []

        def place(task: Task, start: int, reason: str) -> None:
            """Plan the task at the given start, or skip it if it runs past midnight."""
            end = start + task.duration_minutes
            if end > MINUTES_PER_DAY:
                skipped_items.append({"task": task, "reason": "Would run past midnight"})
                return
            busy_periods.append((start, end))
            planned_items.append(
                {"task": task, "start_time": _to_time(start), "reason": reason}
            )

        for task in with_preference:
            preferred = _to_minutes(task.preferred_time)
            if preferred < day_start:
                reason = (
                    f"{task.priority.capitalize()} priority, moved to the start of "
                    f"the day because {task.preferred_time:%H:%M} is too early"
                )
            else:
                reason = f"{task.priority.capitalize()} priority, at its preferred time"
            place(task, max(preferred, day_start), reason)

        for task in without_preference:
            start = self._earliest_free_start(
                day_start, task.duration_minutes, busy_periods
            )
            reason = f"{task.priority.capitalize()} priority, in the next free slot"
            place(task, start, reason)

        planned_items.sort(key=lambda item: item["start_time"])
        return planned_items, skipped_items

    def _earliest_free_start(
        self, earliest: int, duration: int, busy_periods: list[tuple[int, int]]
    ) -> int:
        """Return the first start, in minutes, that avoids all the busy periods."""
        start = earliest
        for busy_start, busy_end in sorted(busy_periods):
            if start + duration <= busy_start:
                break
            start = max(start, busy_end)
        return start

    def detect_conflicts(self) -> list[str]:
        """Return a warning for each pair of planned items that overlap in time."""
        items = sorted(self.planned_items, key=lambda item: item["start_time"])
        conflicts = []
        for index, first in enumerate(items):
            first_start = _to_minutes(first["start_time"])
            first_end = first_start + first["task"].duration_minutes
            for second in items[index + 1:]:
                if _to_minutes(second["start_time"]) >= first_end:
                    break
                conflicts.append(self._conflict_warning(first, second))
        return conflicts

    def _conflict_warning(self, first: dict, second: dict) -> str:
        """Return a warning describing how two planned items clash."""
        first_start = f"{first['start_time']:%H:%M}"
        second_start = f"{second['start_time']:%H:%M}"
        if first_start == second_start:
            timing = f"both start at {first_start}"
        else:
            timing = f"overlap ({first_start} and {second_start})"
        same_pet = first["task"].pet_name == second["task"].pet_name
        pets = "same pet" if same_pet else "different pets"
        return (
            f"Warning: {self._label(first['task'])} and "
            f"{self._label(second['task'])} {timing} [{pets}]"
        )

    def total_minutes(self) -> int:
        """Return the total minutes of all planned items."""
        return sum(item["task"].duration_minutes for item in self.planned_items)

    def explain_plan(self) -> str:
        """Return a plain-language explanation of the plan."""
        if self.plan_date is None:
            return "No plan has been generated yet."

        lines = [
            f"Plan for {self.plan_date}: {len(self.planned_items)} task(s) using "
            f"{self.total_minutes()} of {self.owner.available_minutes} available minutes."
        ]
        for item in self.planned_items:
            lines.append(
                f"- {item['start_time']:%H:%M} {self._label(item['task'])}: "
                f"{item['reason']}"
            )
        if self.skipped_items:
            lines.append("Skipped:")
            for item in self.skipped_items:
                lines.append(f"- {self._label(item['task'])}: {item['reason']}")
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("Conflicts:")
            lines.extend(f"- {conflict}" for conflict in conflicts)
        return "\n".join(lines)

    def display_plan(self) -> str:
        """Return the plan formatted for reading."""
        if self.plan_date is None:
            return "No plan has been generated yet."

        lines = [f"Daily plan for {self.owner.name} ({self.plan_date}):"]
        if not self.planned_items:
            lines.append("  No tasks planned.")
        for item in self.planned_items:
            task = item["task"]
            lines.append(
                f"  {item['start_time']:%H:%M} - {self._label(task)} "
                f"({task.duration_minutes} min) [priority: {task.priority}]"
            )
        return "\n".join(lines)

    def _label(self, task: Task) -> str:
        """Return the task's title with its pet's name, if it has one."""
        return f"{task.title} ({task.pet_name})" if task.pet_name else task.title
