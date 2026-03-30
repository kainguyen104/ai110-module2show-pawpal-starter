from pawpal_system import Pet, Task, TaskCategory


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
