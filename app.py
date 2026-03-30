import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task, TaskCategory


def _priority_to_score(priority_label: str) -> int:
    """Convert UI priority labels into numeric scheduler priority."""
    mapping = {"low": 1, "medium": 3, "high": 5}
    return mapping.get(priority_label, 3)


def _get_active_pet(owner: Owner, pet_id: str) -> Pet | None:
    """Return the active pet object by ID from the owner record."""
    for pet in owner.pets:
        if pet.pet_id == pet_id:
            return pet
    return None


def _init_session_state() -> None:
    """Create core app objects once and keep them in the Streamlit session vault."""
    if "owner" not in st.session_state:
        st.session_state["owner"] = Owner(
            owner_id="owner-1",
            name="Jordan",
            daily_time_available_minutes=60,
        )

    if "active_pet_id" not in st.session_state:
        default_pet = Pet(pet_id="pet-1", name="Mochi", species="dog", age=3)
        st.session_state["owner"].add_pet(default_pet)
        st.session_state["active_pet_id"] = default_pet.pet_id


def _next_pet_id(owner: Owner) -> str:
    """Return the next available pet ID for this owner."""
    return f"pet-{len(owner.pets) + 1}"


def _next_task_id(owner: Owner) -> str:
    """Return the next available task ID across all pets."""
    return f"task-{len(owner.list_all_tasks()) + 1}"


_init_session_state()
owner: Owner = st.session_state["owner"]
active_pet = _get_active_pet(owner, st.session_state["active_pet_id"])

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner and Pets")
owner_name = st.text_input("Owner name", value=owner.name)
available_minutes = st.number_input(
    "Daily available minutes",
    min_value=0,
    max_value=600,
    value=owner.daily_time_available_minutes,
)

if st.button("Save owner profile"):
    owner.name = owner_name
    owner.daily_time_available_minutes = int(available_minutes)
    st.success("Owner profile saved in session state.")

with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("New pet name")
    new_pet_species = st.selectbox("New pet species", ["dog", "cat", "other"])
    new_pet_age = st.number_input("New pet age", min_value=0, max_value=40, value=1)
    submit_add_pet = st.form_submit_button("Add pet")

if submit_add_pet:
    if not new_pet_name.strip():
        st.error("Pet name is required.")
    else:
        new_pet = Pet(
            pet_id=_next_pet_id(owner),
            name=new_pet_name.strip(),
            species=new_pet_species,
            age=int(new_pet_age),
        )
        owner.add_pet(new_pet)
        st.session_state["active_pet_id"] = new_pet.pet_id
        st.success(f"Added pet {new_pet.name}.")

pet_options = {f"{pet.name} ({pet.species})": pet.pet_id for pet in owner.pets}
if pet_options:
    pet_labels = list(pet_options.keys())
    current_pet_id = st.session_state["active_pet_id"]
    current_index = next(
        (idx for idx, label in enumerate(pet_labels) if pet_options[label] == current_pet_id),
        0,
    )
    selected_label = st.selectbox("Active pet", pet_labels, index=current_index)
    st.session_state["active_pet_id"] = pet_options[selected_label]
    active_pet = _get_active_pet(owner, st.session_state["active_pet_id"])
else:
    active_pet = None

st.markdown("### Tasks")
st.caption("Add a task to the active pet.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    category_label = st.selectbox(
        "Category",
        ["walk", "feeding", "meds", "enrichment", "grooming", "other"],
        index=5,
    )

if st.button("Add task to active pet"):
    if active_pet is None:
        st.error("No active pet found in session state.")
    else:
        active_pet.add_task(
            Task(
                task_id=_next_task_id(owner),
                pet_id=active_pet.pet_id,
                title=task_title,
                category=TaskCategory(category_label),
                duration_minutes=int(duration),
                priority=_priority_to_score(priority),
                is_recurring=True,
                frequency="daily",
            )
        )
        st.success(f"Task added to {active_pet.name}.")

task_rows = []
if active_pet is not None:
    for task in active_pet.list_tasks():
        task_rows.append(
            {
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "status": task.status,
            }
        )

if task_rows:
    st.write("Current tasks:")
    st.table(task_rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily schedule using your Scheduler class.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()
    summary = scheduler.get_plan_summary()

    st.write("### Today's Schedule")
    st.write(
        f"Planned: {summary['planned_count']} tasks | "
        f"Deferred: {summary['deferred_count']} tasks"
    )

    if summary["planned_tasks"]:
        st.write("Planned tasks")
        st.table(summary["planned_tasks"])
    else:
        st.info("No planned tasks for today.")

    if summary["deferred_tasks"]:
        st.write("Deferred tasks")
        st.table(summary["deferred_tasks"])

    st.write("Why this plan")
    st.text(summary["explanation"])
