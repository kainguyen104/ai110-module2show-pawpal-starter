from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task, TaskCategory


def test_task_completion_updates_status() -> None:
    task = Task(
        task_id="task-1",
        pet_id="pet-1",
        title="Morning walk",
        category=TaskCategory.WALK,
        duration_minutes=20,
        priority=3,
    )

    task.mark_complete()

    assert task.status == "completed"


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(pet_id="pet-1", name="Mochi", species="dog", age=4)
    initial_count = len(pet.tasks)

    pet.add_task(
        Task(
            task_id="task-2",
            pet_id="pet-1",
            title="Evening feeding",
            category=TaskCategory.FEEDING,
            duration_minutes=15,
            priority=2,
        )
    )

    assert len(pet.tasks) == initial_count + 1


def test_sorting_correctness_returns_chronological_order() -> None:
    owner = Owner(owner_id="owner-1", name="Jordan", daily_time_available_minutes=60)
    pet = Pet(pet_id="pet-1", name="Mochi", species="dog", age=4)
    owner.add_pet(pet)

    pet.add_task(
        Task(
            task_id="task-1",
            pet_id="pet-1",
            title="Late walk",
            category=TaskCategory.WALK,
            duration_minutes=20,
            priority=2,
            time="18:30",
        )
    )
    pet.add_task(
        Task(
            task_id="task-2",
            pet_id="pet-1",
            title="Morning meds",
            category=TaskCategory.MEDS,
            duration_minutes=10,
            priority=5,
            time="08:15",
        )
    )
    pet.add_task(
        Task(
            task_id="task-3",
            pet_id="pet-1",
            title="Lunch feeding",
            category=TaskCategory.FEEDING,
            duration_minutes=15,
            priority=3,
            time="12:00",
        )
    )

    scheduler = Scheduler(owner=owner)
    sorted_tasks = scheduler.sort_by_time(owner.list_all_tasks())

    assert [task.time for task in sorted_tasks] == ["08:15", "12:00", "18:30"]


def test_recurrence_logic_daily_completion_creates_next_day_task() -> None:
    owner = Owner(owner_id="owner-1", name="Jordan", daily_time_available_minutes=60)
    pet = Pet(pet_id="pet-1", name="Mochi", species="dog", age=4)
    owner.add_pet(pet)

    due_today = date.today()
    pet.add_task(
        Task(
            task_id="task-1",
            pet_id="pet-1",
            title="Daily walk",
            category=TaskCategory.WALK,
            duration_minutes=20,
            priority=3,
            due_date=due_today,
            frequency="daily",
            is_recurring=True,
        )
    )

    scheduler = Scheduler(owner=owner)
    next_task = scheduler.mark_task_complete("task-1")

    assert next_task is not None
    assert next_task.due_date == due_today + timedelta(days=1)
    assert next_task.status == "pending"
    assert pet.get_task("task-1").status == "completed"


def test_conflict_detection_flags_duplicate_times() -> None:
    owner = Owner(owner_id="owner-1", name="Jordan", daily_time_available_minutes=60)
    dog = Pet(pet_id="pet-1", name="Mochi", species="dog", age=4)
    cat = Pet(pet_id="pet-2", name="Luna", species="cat", age=2)
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(
        Task(
            task_id="task-1",
            pet_id="pet-1",
            title="Meds",
            category=TaskCategory.MEDS,
            duration_minutes=10,
            priority=5,
            time="08:15",
        )
    )
    cat.add_task(
        Task(
            task_id="task-2",
            pet_id="pet-2",
            title="Feeding",
            category=TaskCategory.FEEDING,
            duration_minutes=10,
            priority=4,
            time="08:15",
        )
    )

    scheduler = Scheduler(owner=owner)
    warnings = scheduler.detect_time_conflicts(owner.list_all_tasks())

    assert len(warnings) == 1
    assert "Time conflict at 08:15" in warnings[0]
