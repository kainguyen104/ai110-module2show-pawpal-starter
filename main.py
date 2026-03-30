from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task, TaskCategory


def build_sample_owner() -> Owner:
	owner = Owner(
		owner_id="owner-1",
		name="Jordan",
		daily_time_available_minutes=60,
		preferences={
			"priority_weight": 10,
			"duration_penalty": 0.08,
			"category_boosts": {"meds": 8, "feeding": 5, "walk": 3},
		},
	)

	dog = Pet(pet_id="pet-1", name="Mochi", species="dog", age=4)
	cat = Pet(pet_id="pet-2", name="Luna", species="cat", age=2)

	owner.add_pet(dog)
	owner.add_pet(cat)

	dog.add_task(
		Task(
			task_id="task-1",
			pet_id="pet-1",
			title="Morning walk",
			category=TaskCategory.WALK,
			duration_minutes=25,
			priority=3,
			time="14:30",
			is_recurring=True,
		)
	)
	dog.add_task(
		Task(
			task_id="task-2",
			pet_id="pet-1",
			title="Give heartworm meds",
			category=TaskCategory.MEDS,
			duration_minutes=10,
			priority=5,
			time="08:15",
			due_date=date.today(),
		)
	)
	cat.add_task(
		Task(
			task_id="task-3",
			pet_id="pet-2",
			title="Evening feeding",
			category=TaskCategory.FEEDING,
			duration_minutes=15,
			priority=4,
			time="08:15",
			is_recurring=True,
		)
	)
	cat.add_task(
		Task(
			task_id="task-4",
			pet_id="pet-2",
			title="Play enrichment game",
			category=TaskCategory.ENRICHMENT,
			duration_minutes=12,
			priority=2,
			time="07:45",
			is_recurring=True,
		)
	)

	# Mark one task complete so filtering by status can be demonstrated.
	completed_task = dog.get_task("task-1")
	if completed_task is not None:
		completed_task.mark_complete()

	return owner


def print_todays_schedule() -> None:
	owner = build_sample_owner()
	scheduler = Scheduler(owner=owner, plan_date=date.today())
	all_tasks = scheduler.retrieve_all_tasks()
	tasks_sorted_by_time = scheduler.sort_by_time(all_tasks)
	completed_tasks = scheduler.filter_tasks(tasks=all_tasks, status="completed")
	luna_tasks = scheduler.filter_tasks(tasks=all_tasks, pet_name="Luna")

	print("Tasks Sorted By Time")
	print("=" * 20)
	for task in tasks_sorted_by_time:
		print(f"- {task.time} | {task.title} | Pet {task.pet_id} | {task.status}")
	print()

	print("Completed Tasks")
	print("=" * 15)
	if completed_tasks:
		for task in completed_tasks:
			print(f"- {task.title} at {task.time}")
	else:
		print("- None")
	print()

	print("Tasks Filtered By Pet Name (Luna)")
	print("=" * 33)
	if luna_tasks:
		for task in luna_tasks:
			print(f"- {task.time} | {task.title} | status={task.status}")
	else:
		print("- None")
	print()

	conflict_warnings = scheduler.detect_time_conflicts(all_tasks)
	print("Conflict Warnings")
	print("=" * 17)
	if conflict_warnings:
		for warning in conflict_warnings:
			print(f"- WARNING: {warning}")
	else:
		print("- None")
	print()

	scheduler.build_plan()
	summary = scheduler.get_plan_summary()

	print("Today's Schedule")
	print("=" * 16)
	print(f"Owner: {owner.name}")
	print(f"Date: {summary['date']}")
	print(f"Available time: {summary['available_minutes']} minutes")
	print()

	print("Planned Tasks:")
	if not summary["planned_tasks"]:
		print("- None")
	else:
		for task in summary["planned_tasks"]:
			print(
				f"- {task['title']} (Pet {task['pet_id']}) | "
				f"{task['duration_minutes']}m | Priority {task['priority']}"
			)

	print()
	print("Deferred Tasks:")
	if not summary["deferred_tasks"]:
		print("- None")
	else:
		for task in summary["deferred_tasks"]:
			print(
				f"- {task['title']} (Pet {task['pet_id']}) | "
				f"{task['duration_minutes']}m | Priority {task['priority']}"
			)


if __name__ == "__main__":
	print_todays_schedule()