from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

PRIORITIES = ["low", "medium", "high"]
FREQUENCIES = ["daily", "weekly"]


def format_time(clock_time):
    """Return a time as HH:MM, or "Any time" if there isn't one."""
    return clock_time.strftime("%H:%M") if clock_time else "Any time"


def task_status(task, day):
    """Return a short description of where the task stands on the given day."""
    if task.is_complete():
        return f"Done {task.last_completed}"
    return "Due today" if task.is_due(day) else f"Due {task.due_date}"


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** helps you stay on top of pet care. Add your pets and their tasks, then
generate a plan for today based on your available time and each task's priority.
"""
)

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Minutes available today", min_value=1, max_value=1440, value=90
)

# Create the Owner once, then reuse it on every rerun so its pets and tasks persist.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, int(available_minutes))
owner = st.session_state.owner
owner.name = owner_name
owner.available_minutes = int(available_minutes)

scheduler = Scheduler(owner)
today = date.today()

st.markdown("### Pets")

with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_submitted = st.form_submit_button("Add pet")

if pet_submitted:
    pet_name = new_pet_name.strip()
    if not pet_name:
        st.warning("Enter a pet name.")
    elif pet_name.lower() in [pet.name.lower() for pet in owner.pets]:
        st.warning(f"{pet_name} has already been added.")
    else:
        owner.add_pet(Pet(pet_name, species))

if owner.pets:
    st.table([{"Name": pet.name, "Species": pet.species} for pet in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_name = st.selectbox("Pet", [pet.name for pet in owner.pets])
        col1, col2, col3 = st.columns(3)
        with col1:
            new_task_title = st.text_input("Task title")
        with col2:
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
        with col3:
            priority = st.selectbox("Priority", PRIORITIES, index=2)
        col4, col5 = st.columns(2)
        with col4:
            frequency = st.selectbox("Frequency", FREQUENCIES)
        with col5:
            preferred_time = st.time_input(
                "Preferred time (optional)", value=None, step=300
            )
        task_submitted = st.form_submit_button("Add task")

    if task_submitted:
        task_title = new_task_title.strip()
        if task_title:
            selected_pet = next(
                pet for pet in owner.pets if pet.name == selected_pet_name
            )
            selected_pet.add_task(
                Task(
                    task_title,
                    int(duration),
                    priority,
                    frequency=frequency,
                    preferred_time=preferred_time,
                )
            )
        else:
            st.warning("Enter a task title.")
else:
    st.info("Add a pet before adding tasks.")

due_tasks = scheduler.sort_by_time(owner.get_tasks_due(today))
if due_tasks:
    with st.form("complete_task_form"):
        task_index = st.selectbox(
            "Task due today",
            range(len(due_tasks)),
            format_func=lambda index: (
                f"{due_tasks[index].title} ({due_tasks[index].pet_name})"
            ),
        )
        complete_submitted = st.form_submit_button("Mark complete")

    if complete_submitted:
        completed_task = due_tasks[task_index]
        next_task = scheduler.mark_task_complete(completed_task, today)
        st.session_state.task_message = (
            f"{completed_task.title} is done. It's next due on {next_task.due_date}."
        )
        # Rerun so the dropdown above can't still list the task that was just finished.
        st.rerun()

open_tasks = scheduler.sort_by_time(owner.filter_tasks(completed=False))
if open_tasks:
    with st.expander("Edit or remove a task"):
        edit_index = st.selectbox(
            "Task to change",
            range(len(open_tasks)),
            format_func=lambda index: (
                f"{open_tasks[index].title} ({open_tasks[index].pet_name}) - "
                f"{task_status(open_tasks[index], today)}"
            ),
        )
        edited_task = open_tasks[edit_index]
        task_id = id(edited_task)

        with st.form(f"edit_task_form_{task_id}"):
            new_title = st.text_input(
                "New title", value=edited_task.title, key=f"title_{task_id}"
            )
            new_duration = st.number_input(
                "New duration (minutes)",
                min_value=1,
                max_value=240,
                value=edited_task.duration_minutes,
                key=f"duration_{task_id}",
            )
            new_priority = st.selectbox(
                "New priority",
                PRIORITIES,
                index=PRIORITIES.index(edited_task.priority),
                key=f"priority_{task_id}",
            )
            new_frequency = st.selectbox(
                "New frequency",
                FREQUENCIES,
                index=FREQUENCIES.index(edited_task.frequency),
                key=f"frequency_{task_id}",
            )
            new_time = st.time_input(
                "New preferred time",
                value=edited_task.preferred_time or time(8, 0),
                step=300,
                key=f"time_{task_id}",
            )
            any_time = st.checkbox(
                "Any time (no preferred time)",
                value=edited_task.preferred_time is None,
                key=f"any_time_{task_id}",
            )
            save_submitted = st.form_submit_button("Save changes")
            remove_submitted = st.form_submit_button("Remove task")

        if save_submitted:
            cleaned_title = new_title.strip()
            if cleaned_title:
                edited_task.update(
                    {
                        "title": cleaned_title,
                        "duration_minutes": int(new_duration),
                        "priority": new_priority,
                        "frequency": new_frequency,
                        "preferred_time": None if any_time else new_time,
                    }
                )
                st.session_state.task_message = f"{cleaned_title} was updated."
                st.rerun()
            else:
                st.warning("Enter a task title.")

        if remove_submitted:
            task_owner = next(pet for pet in owner.pets if edited_task in pet.tasks)
            task_owner.remove_task(edited_task)
            st.session_state.task_message = f"{edited_task.title} was removed."
            st.rerun()

if "task_message" in st.session_state:
    st.success(st.session_state.pop("task_message"))

if owner.get_all_tasks():
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_choice = st.selectbox(
            "Show pet", ["All pets"] + [pet.name for pet in owner.pets]
        )
    with filter_col2:
        status_choice = st.selectbox("Show status", ["Due today", "Completed", "All"])

    status_filters = {
        "Due today": {"completed": False, "day": today},
        "Completed": {"completed": True},
        "All": {},
    }
    matching_tasks = owner.filter_tasks(
        pet_name=None if pet_choice == "All pets" else pet_choice,
        **status_filters[status_choice],
    )

    if matching_tasks:
        st.write("Current tasks, sorted by preferred time:")
        st.table(
            [
                {
                    "Preferred time": format_time(task.preferred_time),
                    "Pet": task.pet_name,
                    "Task": task.title,
                    "Duration (minutes)": task.duration_minutes,
                    "Priority": task.priority,
                    "Frequency": task.frequency,
                    "Status": task_status(task, today),
                }
                for task in scheduler.sort_by_time(matching_tasks)
            ]
        )
    else:
        st.info("No tasks match these filters.")
elif owner.pets:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Creates today's plan from your tasks, priorities and available time.")

if st.button("Generate schedule"):
    scheduler.generate_plan(today)

    if scheduler.planned_items:
        st.success(
            f"Planned {len(scheduler.planned_items)} task(s) using "
            f"{scheduler.total_minutes()} of {owner.available_minutes} available minutes."
        )
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            conflict_list = "\n".join(
                f"- {conflict.removeprefix('Warning: ')}" for conflict in conflicts
            )
            st.warning(
                f"**{len(conflicts)} time conflict(s) in this plan.** You can't do "
                f"these at the same time, so move one under **Edit or remove a task**.\n\n"
                f"{conflict_list}",
                icon="⚠️",
            )
        st.table(
            [
                {
                    "Time": format_time(item["start_time"]),
                    "Pet": item["task"].pet_name,
                    "Task": item["task"].title,
                    "Duration (minutes)": item["task"].duration_minutes,
                    "Priority": item["task"].priority,
                    "Why": item["reason"],
                }
                for item in scheduler.planned_items
            ]
        )

    if scheduler.skipped_items:
        st.write("Skipped tasks:")
        st.table(
            [
                {
                    "Pet": item["task"].pet_name,
                    "Task": item["task"].title,
                    "Why": item["reason"],
                }
                for item in scheduler.skipped_items
            ]
        )

    if not scheduler.planned_items and not scheduler.skipped_items:
        st.info("No tasks to plan yet. Add a task above.")
