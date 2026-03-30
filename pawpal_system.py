"""PawPal+ core system skeleton.

This module defines the backend class structure for the scheduling logic layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
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
	time: str = "09:00"
	frequency: str = "once"
	due_date: date | None = None
	is_recurring: bool = False
	status: str = "pending"

	@property
	def description(self) -> str:
		"""Compatibility alias for task text."""
		return self.title

	@property
	def completed(self) -> bool:
		"""Return whether the task is completed."""
		return self.status == "completed"

	def mark_complete(self) -> None:
		"""Mark this task as complete."""
		self.status = "completed"

	def update_details(self, updates: dict[str, Any]) -> None:
		"""Update task fields using a dictionary of changes."""
		allowed_fields = {
			"title",
			"category",
			"duration_minutes",
			"priority",
			"time",
			"frequency",
			"due_date",
			"is_recurring",
			"status",
		}
		for key, value in updates.items():
			if key in allowed_fields:
				setattr(self, key, value)

		if self.duration_minutes <= 0:
			raise ValueError("duration_minutes must be greater than 0")
		if self.priority < 0:
			raise ValueError("priority must be non-negative")
		if len(self.time.split(":")) != 2:
			raise ValueError("time must be in HH:MM format")

	def is_due_today(self, target_date: date) -> bool:
		"""Return whether this task is due on the target date."""
		if self.completed and not self.is_recurring:
			return False

		if self.is_recurring:
			return True

		if self.due_date is None:
			return True

		return self.due_date <= target_date

	def score_for_schedule(self, owner_preferences: dict[str, Any]) -> float:
		"""Return a priority score used by the scheduler."""
		priority_weight = float(owner_preferences.get("priority_weight", 10.0))
		duration_penalty = float(owner_preferences.get("duration_penalty", 0.1))
		category_boosts = owner_preferences.get("category_boosts", {})
		category_boost = float(category_boosts.get(self.category.value, 0.0))

		# Higher priority and preferred categories rank earlier; long tasks are mildly penalized.
		return (self.priority * priority_weight) + category_boost - (
			self.duration_minutes * duration_penalty
		)


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
		if task.pet_id != self.pet_id:
			raise ValueError("task.pet_id does not match this pet")
		if self.get_task(task.task_id) is not None:
			raise ValueError(f"Task with id '{task.task_id}' already exists")
		self.tasks.append(task)

	def get_task(self, task_id: str) -> Task | None:
		"""Fetch a task by ID, if present."""
		for task in self.tasks:
			if task.task_id == task_id:
				return task
		return None

	def edit_task(self, task_id: str, updates: dict[str, Any]) -> None:
		"""Edit an existing task by ID."""
		task = self.get_task(task_id)
		if task is None:
			raise ValueError(f"Task with id '{task_id}' was not found")
		task.update_details(updates)

	def remove_task(self, task_id: str) -> None:
		"""Remove a task by ID."""
		task = self.get_task(task_id)
		if task is None:
			raise ValueError(f"Task with id '{task_id}' was not found")
		self.tasks.remove(task)

	def list_tasks(self) -> list[Task]:
		"""Return all tasks assigned to this pet."""
		return list(self.tasks)


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
		if any(existing_pet.pet_id == pet.pet_id for existing_pet in self.pets):
			raise ValueError(f"Pet with id '{pet.pet_id}' already exists")
		self.pets.append(pet)

	def update_preferences(self, preferences: dict[str, Any]) -> None:
		"""Update owner scheduling preferences."""
		self.preferences.update(preferences)

	def get_available_time(self) -> int:
		"""Return the owner's daily available time in minutes."""
		return max(self.daily_time_available_minutes, 0)

	def list_all_tasks(self) -> list[Task]:
		"""Return all tasks across all owned pets."""
		all_tasks: list[Task] = []
		for pet in self.pets:
			all_tasks.extend(pet.list_tasks())
		return all_tasks


class Scheduler:
	"""Builds a daily plan from pets, tasks, and constraints."""

	def __init__(self, owner: Owner, plan_date: date | None = None, pets: list[Pet] | None = None) -> None:
		"""Initialize scheduler state for the selected owner and date."""
		self.owner = owner
		# Default to the owner's pets to keep ownership relationships consistent.
		self.pets = pets if pets is not None else owner.pets
		self.date = plan_date if plan_date is not None else date.today()
		self.candidate_tasks: list[Task] = []
		self.planned_tasks: list[Task] = []
		self.deferred_tasks: list[Task] = []
		self.explanation_log: list[str] = []

	def retrieve_all_tasks(self) -> list[Task]:
		"""Retrieve tasks from owner-pet relationships for scheduling."""
		if self.pets is self.owner.pets:
			return self.owner.list_all_tasks()

		all_tasks: list[Task] = []
		for pet in self.pets:
			all_tasks.extend(pet.list_tasks())
		return all_tasks

	def collect_due_tasks(self) -> list[Task]:
		"""Gather all tasks that should be considered for today."""
		self.candidate_tasks = [
			task for task in self.retrieve_all_tasks() if task.is_due_today(self.date)
		]
		return list(self.candidate_tasks)

	def rank_tasks(self, tasks: list[Task]) -> list[Task]:
		"""Sort tasks by priority and scheduling score."""
		preferences = self.owner.preferences
		return sorted(
			tasks,
			key=lambda task: (
				-task.score_for_schedule(preferences),
				task.duration_minutes,
				task.title.lower(),
			),
		)

	def sort_by_time(self, tasks: list[Task]) -> list[Task]:
		"""Sort task objects by their HH:MM time value."""
		return sorted(tasks, key=lambda task: self._parse_time_to_minutes(task.time))

	def _parse_time_to_minutes(self, hhmm: str) -> int:
		"""Convert HH:MM strings into sortable minute values."""
		parts = hhmm.split(":")
		if len(parts) != 2:
			return 24 * 60 + 1
		hour_text, minute_text = parts
		if not (hour_text.isdigit() and minute_text.isdigit()):
			return 24 * 60 + 1
		hours = int(hour_text)
		minutes = int(minute_text)
		if not (0 <= hours <= 23 and 0 <= minutes <= 59):
			return 24 * 60 + 1
		return hours * 60 + minutes

	def _minutes_to_hhmm(self, total_minutes: int) -> str:
		"""Convert minute counts into HH:MM strings."""
		hours = total_minutes // 60
		minutes = total_minutes % 60
		return f"{hours:02d}:{minutes:02d}"

	def detect_time_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
		"""Return warning messages for tasks that share the exact same start time."""
		source_tasks = tasks if tasks is not None else self.collect_due_tasks()
		sorted_tasks = self.sort_by_time(source_tasks)
		warnings: list[str] = []

		for first_index in range(len(sorted_tasks)):
			first_task = sorted_tasks[first_index]
			for second_index in range(first_index + 1, len(sorted_tasks)):
				second_task = sorted_tasks[second_index]
				if second_task.time != first_task.time:
					break
				warnings.append(
					f"Time conflict at {first_task.time}: '{first_task.title}' (pet {first_task.pet_id}) "
					f"and '{second_task.title}' (pet {second_task.pet_id})."
				)

		return warnings

	def filter_tasks(
		self,
		tasks: list[Task] | None = None,
		status: str | None = None,
		pet_name: str | None = None,
	) -> list[Task]:
		"""Filter tasks by completion status and/or pet name."""
		source = tasks if tasks is not None else self.retrieve_all_tasks()
		pet_lookup = {pet.pet_id: pet.name.lower() for pet in self.owner.pets}
		status_normalized = status.lower() if status else None
		pet_name_normalized = pet_name.lower() if pet_name else None

		return [
			task
			for task in source
			if (status_normalized is None or task.status.lower() == status_normalized)
			and (
				pet_name_normalized is None
				or pet_lookup.get(task.pet_id, "") == pet_name_normalized
			)
		]

	def find_next_available_slot(
		self,
		duration_minutes: int,
		window_start: str = "06:00",
		window_end: str = "22:00",
		tasks: list[Task] | None = None,
		buffer_minutes: int = 0,
	) -> str | None:
		"""Return the earliest available HH:MM slot that can fit the requested duration."""
		if duration_minutes <= 0:
			raise ValueError("duration_minutes must be greater than 0")
		if buffer_minutes < 0:
			raise ValueError("buffer_minutes must be non-negative")

		window_start_min = self._parse_time_to_minutes(window_start)
		window_end_min = self._parse_time_to_minutes(window_end)
		if window_start_min > 24 * 60 or window_end_min > 24 * 60:
			return None
		if window_start_min >= window_end_min:
			return None

		source_tasks = tasks if tasks is not None else self.collect_due_tasks()
		occupied_intervals: list[tuple[int, int]] = []

		for task in source_tasks:
			start_min = self._parse_time_to_minutes(task.time)
			if start_min > 24 * 60:
				continue
			task_duration = max(task.duration_minutes, 0)
			end_min = start_min + task_duration

			expanded_start = max(window_start_min, start_min - buffer_minutes)
			expanded_end = min(window_end_min, end_min + buffer_minutes)
			if expanded_end > expanded_start:
				occupied_intervals.append((expanded_start, expanded_end))

		occupied_intervals.sort(key=lambda interval: interval[0])
		merged: list[tuple[int, int]] = []
		for start_min, end_min in occupied_intervals:
			if not merged or start_min > merged[-1][1]:
				merged.append((start_min, end_min))
			else:
				last_start, last_end = merged[-1]
				merged[-1] = (last_start, max(last_end, end_min))

		candidate_start = window_start_min
		for busy_start, busy_end in merged:
			if busy_start - candidate_start >= duration_minutes:
				return self._minutes_to_hhmm(candidate_start)
			candidate_start = max(candidate_start, busy_end)

		if window_end_min - candidate_start >= duration_minutes:
			return self._minutes_to_hhmm(candidate_start)

		return None

	def build_plan(self) -> list[Task]:
		"""Create the daily schedule based on time and priorities."""
		self.explanation_log = []
		self.planned_tasks = []
		self.deferred_tasks = []

		tasks_to_schedule = self.rank_tasks(self.collect_due_tasks())
		conflict_warnings = self.detect_time_conflicts(tasks_to_schedule)
		for warning in conflict_warnings:
			self.explanation_log.append(f"Warning: {warning}")
		remaining_minutes = self.owner.get_available_time()

		for task in tasks_to_schedule:
			if task.duration_minutes <= remaining_minutes:
				self.planned_tasks.append(task)
				remaining_minutes -= task.duration_minutes
				self.explanation_log.append(
					f"Planned '{task.title}' for pet {task.pet_id}: priority={task.priority}, "
					f"duration={task.duration_minutes}m, remaining_time={remaining_minutes}m"
				)
			else:
				self.deferred_tasks.append(task)
				self.explanation_log.append(
					f"Deferred '{task.title}' for pet {task.pet_id}: needs {task.duration_minutes}m "
					f"but only {remaining_minutes}m left"
				)

		if not tasks_to_schedule:
			self.explanation_log.append("No due tasks found for the selected date.")

		return list(self.planned_tasks)

	def mark_task_complete(self, task_id: str) -> Task | None:
		"""Mark a task complete and create the next recurring instance when applicable."""
		for pet in self.owner.pets:
			task = pet.get_task(task_id)
			if task is None:
				continue

			task.mark_complete()
			next_task = self._create_next_recurring_task(task)
			if next_task is not None:
				pet.add_task(next_task)
				self.explanation_log.append(
					f"Recurring task created: '{next_task.title}' due {next_task.due_date}"
				)
			return next_task

		raise ValueError(f"Task with id '{task_id}' was not found")

	def _create_next_recurring_task(self, task: Task) -> Task | None:
		"""Create the next task instance for daily or weekly recurring tasks."""
		frequency = task.frequency.lower().strip()
		if frequency not in {"daily", "weekly"}:
			return None

		base_date = task.due_date if task.due_date is not None else date.today()
		delta = timedelta(days=1) if frequency == "daily" else timedelta(days=7)
		next_due_date = base_date + delta

		all_tasks = self.owner.list_all_tasks()
		next_task_id = f"task-{len(all_tasks) + 1}"

		return Task(
			task_id=next_task_id,
			pet_id=task.pet_id,
			title=task.title,
			category=task.category,
			duration_minutes=task.duration_minutes,
			priority=task.priority,
			time=task.time,
			frequency=task.frequency,
			due_date=next_due_date,
			is_recurring=task.is_recurring,
			status="pending",
		)

	def explain_plan(self) -> str:
		"""Provide a human-readable explanation of scheduling decisions."""
		if not self.explanation_log:
			self.build_plan()
		return "\n".join(self.explanation_log)

	def get_plan_summary(self) -> dict[str, Any]:
		"""Return a summary payload for UI display."""
		planned_duration = sum(task.duration_minutes for task in self.planned_tasks)
		deferred_duration = sum(task.duration_minutes for task in self.deferred_tasks)
		warnings = [
			line.replace("Warning: ", "", 1)
			for line in self.explanation_log
			if line.startswith("Warning: ")
		]

		return {
			"date": self.date.isoformat(),
			"available_minutes": self.owner.get_available_time(),
			"planned_count": len(self.planned_tasks),
			"deferred_count": len(self.deferred_tasks),
			"planned_duration_minutes": planned_duration,
			"deferred_duration_minutes": deferred_duration,
			"warnings": warnings,
			"planned_tasks": [
				{
					"task_id": task.task_id,
					"pet_id": task.pet_id,
					"title": task.title,
					"priority": task.priority,
					"duration_minutes": task.duration_minutes,
				}
				for task in self.planned_tasks
			],
			"deferred_tasks": [
				{
					"task_id": task.task_id,
					"pet_id": task.pet_id,
					"title": task.title,
					"priority": task.priority,
					"duration_minutes": task.duration_minutes,
				}
				for task in self.deferred_tasks
			],
			"explanation": self.explain_plan(),
		}


# Backward compatibility with the earlier class name from the UML skeleton.
DailyScheduler = Scheduler
