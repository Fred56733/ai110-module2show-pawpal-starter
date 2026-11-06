# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. **Add a pet and owner profile:** The user enters basic information about themselves and their pet, such as the pet's name and species and how much time they have available each day. This gives the planner the context it needs.
2. **Add and manage care tasks:** The user creates tasks such as walks, feeding, meds, enrichment or grooming, giving each one a duration and priority. They can edit these tasks later as their pet's routine changes.
3. **Generate and view today's plan:** The user asks for a daily schedule and sees which tasks fit in the time available and in what order. The app also explains its choices, such as why a high-priority task came first or why another task was left out.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML has four classes. `Owner` and `Pet` hold the information about who is involved, `Task` describes the care work, and `Scheduler` makes the planning decisions. An owner can have many pets and each pet can have many tasks, so the design supports households with more than one pet. The scheduler keeps a reference to the owner and reaches the tasks through it.

- **Owner:** Stores the owner's name, the time they have available each day, when their day starts and their preferences. It manages the list of pets and gathers tasks across all of them.
- **Pet:** Stores the pet's name, species, age and care tasks. It adds and removes tasks and reports which ones are due on a given day.
- **Task:** Represents one care activity, with a title, category, duration, priority, frequency, optional preferred time and the date it was last completed. It can update its own details, record when it was completed, work out whether it is due and convert its priority to a number for sorting.
- **Scheduler:** Builds the plan for a day. It sorts the tasks, keeps the ones that fit in the available time and checks for conflicts. It also stores the planned and skipped tasks with a reason for each, so it can explain and display the plan.

I first considered a fifth class, `DailyPlan`, to hold the finished schedule. I folded it into `Scheduler` to keep to the four classes the project called for.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. I asked my AI assistant to review the class skeleton for missing relationships and logic bottlenecks, and I made four changes based on that review:

- **Added `pet_name` to `Task`:** A flat list of tasks lost track of which pet each one belonged to, so two pets' "Feeding" tasks looked identical in the plan. `Pet` now sets this field when a task is added.
- **Added `Owner.get_tasks_due(day)`:** Only `Pet` could filter tasks by day, so the scheduler would have had to loop through the pets itself. This keeps that work in `Owner`.
- **Added `Scheduler.assign_times(tasks)`:** Nothing in the original design gave a task its start time. This method keeps each preferred time and fits the other tasks into free gaps, which also gives `detect_conflicts` real overlaps to find.
- **Changed `fit_tasks` to return skipped tasks too:** It originally returned only the tasks that fit, so the plan couldn't explain what it left out or why.

The design kept changing as I added features. To support recurring tasks, each `Task` became a single occurrence with a `due_date`, and I added `is_complete()`, `next_occurrence()` and `Scheduler.mark_task_complete()`. The scheduler now adds the next occurrence to a pet, so it depends on `Pet` directly, and I added that relationship to the final UML. Testing led to one more change: `Task` now compares by identity instead of by its details, because identical tasks on two pets with the same name were being treated as the same task.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers these constraints:

- **Available time:** The plan can't use more than the owner's available minutes.
- **Priority:** Higher-priority tasks are considered first, and shorter tasks go first within the same priority.
- **Preferred time:** A task with a preferred time keeps it, and other tasks fill the free gaps.
- **Due date and frequency:** Only tasks that are due that day are planned.
- **Time of day:** Tasks can't start before the owner's day starts or run past midnight.

`Owner` also has a `preferences` field, but the scheduler doesn't use it yet.

I decided available time and priority mattered most because a busy owner often can't do everything. Essential care like medication and feeding should make it into the plan before optional tasks like grooming. Preferred time comes after those two because it decides when a task happens, not whether it happens.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler warns about conflicts instead of fixing them. When two tasks have preferred times that overlap, it keeps both at their requested times and adds a warning to the plan, rather than moving one of them to a free slot. The downside is that a plan can contain two things the owner can't do at once, so they have to sort that out themselves.

This is reasonable because a preferred time often matters. Medication may need to happen at a specific time, and moving it automatically could be worse than showing a clear warning. The scheduler can't know which task is safe to move, but the owner does. Tasks without a preferred time are still placed in free gaps automatically, so the owner only has to step in when two fixed times clash.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Claude Code throughout the project. It helped me brainstorm the classes, write the Mermaid UML, generate the skeleton and implement the logic. I also used it to review my design, plan and write tests, debug problems, connect the Streamlit UI and write the documentation. I gave it one step at a time and talked through each result before moving on, which kept me involved in the decisions instead of generating everything at once.

The most helpful prompts were specific and focused on one job. Asking it to review my work and account for any edge cases allow for me to find problems I hadn't noticed, such as nothing assigning start times to tasks. Direct questions helped too, like asking why the scheduler didn't work when the Generate schedule button showed "Not implemented yet".

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

During brainstorming, the AI suggested five classes and recommended keeping a separate `DailyPlan` class. The project called for four classes, so I didn't use that design as-is. `DailyPlan` was folded into `Scheduler`, which now stores the planned and skipped tasks. The same thing happened with recurring tasks: the AI recommended updating a single task, but the project required a new task for each occurrence, so I followed the project.

I verified the AI's work by running it. I checked the terminal output from `main.py`, ran the test suite and tried the app myself. That last step mattered because passing tests didn't mean the app was finished. When I clicked Generate schedule, it still showed a placeholder message, so I asked why and had it connected to the scheduler.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

My 42 tests cover task basics, sorting, building a plan, filtering, recurring tasks and conflict detection. They include normal use and edge cases, such as a pet with no tasks, two tasks at the same time, a task that exactly fills the available time, and dates at the end of a year or on a leap day.

These tests were important because scheduling mistakes are easy to miss when you only look at the output, and a mistake could mean a pet misses its medication. They also found three real bugs:

- A task dropped for running past midnight still used up the available time, so other tasks were skipped for no reason.
- The next occurrence of a task could go to the wrong pet if two pets shared a name and had identical tasks.
- A task completed before its due date came straight back on that same due date.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm fairly confident, about 4 out of 5. All 42 tests pass, and when my AI assistant broke a copy of the code on purpose in 14 different ways, the tests caught every one. I stop at 4 because the automated tests only cover `pawpal_system.py`, not the Streamlit app.

If I had more time, I would add automated tests for the app itself, including editing and removing tasks. I would also test recurring tasks over several weeks, and what happens when the date changes while the app is open.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied that the scheduler explains itself. It doesn't just produce a list. It shows why each task was placed where it was, why anything was skipped and where there are conflicts. I'm also happy with how the tests found real bugs that I wouldn't have noticed just by looking at the output.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would save data so it survives a browser refresh, and let the owner set when their day starts. I would also improve the scheduling logic. Right now a low-priority task with a preferred time can take a slot ahead of a high-priority task without one, and sorting shortest-first can leave out a long but important task. Finally, I would either make owner preferences affect the plan or remove that field.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that working code and a finished product aren't the same thing. My logic passed its tests while the app's main button still did nothing, and I only found that out by using the app myself. AI can move quickly, but I still have to check its work, make the decisions and keep the end user in mind. Working in small steps made that possible.
