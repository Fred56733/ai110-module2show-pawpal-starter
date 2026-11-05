"""PawPal+ logic layer: the backend classes for planning pet care tasks.

This is a skeleton based on diagrams/uml.mmd. Method bodies are not implemented yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


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

    def update(self, details: dict) -> None:
        """Change this task's attributes using the given field names and values."""
        pass

    def mark_complete(self, day: date) -> None:
        """Record that this task was completed on the given day."""
        pass

    def is_due(self, day: date) -> bool:
        """Return True if this task needs doing on the given day."""
        pass

    def priority_rank(self) -> int:
        """Return this task's priority as a number for sorting."""
        pass


@dataclass
class Pet:
    """An animal and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        pass

    def get_tasks_due(self, day: date) -> list[Task]:
        """Return this pet's tasks that are due on the given day."""
        pass


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
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return the tasks for all of this owner's pets."""
        pass


@dataclass
class Scheduler:
    """Builds a daily plan for an owner and explains its choices."""

    owner: Owner
    plan_date: date | None = None
    planned_items: list[dict] = field(default_factory=list)  # task, start time, reason
    skipped_items: list[dict] = field(default_factory=list)  # task, reason

    def generate_plan(self, day: date) -> list[dict]:
        """Build and return the plan for the given day."""
        pass

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks in the order they should be considered."""
        pass

    def fit_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks that fit within the owner's available time."""
        pass

    def detect_conflicts(self) -> list[str]:
        """Return a description of each overlap between planned items."""
        pass

    def total_minutes(self) -> int:
        """Return the total minutes of all planned items."""
        pass

    def explain_plan(self) -> str:
        """Return a plain-language explanation of the plan."""
        pass

    def display_plan(self) -> str:
        """Return the plan formatted for reading."""
        pass
