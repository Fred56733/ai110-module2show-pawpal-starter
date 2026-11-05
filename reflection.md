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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
