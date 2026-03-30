"""PawPal+ core system skeleton.

This module defines the backend class structure for the scheduling logic layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any


class TaskCategory(str, Enum):
	"""Supported task categories for pet care."""

	WALK = "walk"
	FEEDING = "feeding"
	MEDS = "meds"
	ENRICHMENT = "enrichment"
	GROOMING = "grooming"
	OTHER = "other"


@dataclass
class Task:
	"""Represents a single pet care task."""

	task_id: str
	pet_id: str
	title: str
	category: TaskCategory
	duration_minutes: int
	priority: int
	due_date: date | None = None
	is_recurring: bool = False
	status: str = "pending"

	def mark_complete(self) -> None:
		"""Mark this task as complete."""
		pass

	def update_details(self, updates: dict[str, Any]) -> None:
		"""Update task fields using a dictionary of changes."""
		pass

	def is_due_today(self, target_date: date) -> bool:
		"""Return whether this task is due on the target date."""
		pass

	def score_for_schedule(self, owner_preferences: dict[str, Any]) -> float:
		"""Return a priority score used by the scheduler."""
		pass


@dataclass
class Pet:
	"""Represents a pet and its care tasks."""

	pet_id: str
	name: str
	species: str
	age: int
	notes: str = ""
	tasks: list[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		"""Attach a new task to this pet."""
		pass

	def edit_task(self, task_id: str, updates: dict[str, Any]) -> None:
		"""Edit an existing task by ID."""
		pass

	def remove_task(self, task_id: str) -> None:
		"""Remove a task by ID."""
		pass

	def list_tasks(self) -> list[Task]:
		"""Return all tasks assigned to this pet."""
		pass


@dataclass
class Owner:
	"""Represents an owner and planning preferences."""

	owner_id: str
	name: str
	daily_time_available_minutes: int
	preferences: dict[str, Any] = field(default_factory=dict)
	pets: list[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		"""Attach a pet profile to this owner."""
		pass

	def update_preferences(self, preferences: dict[str, Any]) -> None:
		"""Update owner scheduling preferences."""
		pass

	def get_available_time(self) -> int:
		"""Return the owner's daily available time in minutes."""
		pass


class DailyScheduler:
	"""Builds a daily plan from pets, tasks, and constraints."""

	def __init__(self, owner: Owner, pets: list[Pet], plan_date: date) -> None:
		self.owner = owner
		self.pets = pets
		self.date = plan_date
		self.candidate_tasks: list[Task] = []
		self.planned_tasks: list[Task] = []
		self.deferred_tasks: list[Task] = []
		self.explanation_log: list[str] = []

	def collect_due_tasks(self) -> list[Task]:
		"""Gather all tasks that should be considered for today."""
		pass

	def rank_tasks(self, tasks: list[Task]) -> list[Task]:
		"""Sort tasks by priority and scheduling score."""
		pass

	def build_plan(self) -> list[Task]:
		"""Create the daily schedule based on time and priorities."""
		pass

	def explain_plan(self) -> str:
		"""Provide a human-readable explanation of scheduling decisions."""
		pass

	def get_plan_summary(self) -> dict[str, Any]:
		"""Return a summary payload for UI display."""
		pass
