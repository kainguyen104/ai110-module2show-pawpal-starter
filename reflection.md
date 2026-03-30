# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
My initial UML design focused on separating data modeling from scheduling behavior with four core classes plus one enum:
- `TaskCategory` standardizes task types (walk, feeding, meds, enrichment, grooming, other).
- `Task` models one care task with key scheduling inputs such as duration, priority, due date, and completion status.
- `Pet` stores pet profile data and owns a collection of tasks.
- `Owner` stores owner profile data, daily time constraints, and planning preferences.
- `DailyScheduler` coordinates planning by collecting due tasks, ranking them, building a feasible plan, and producing an explanation.
Responsibility split:
- Data-focused classes (`Task`, `Pet`, `Owner`) hold state and basic domain operations.
- `DailyScheduler` contains the plan-generation workflow and decision explanation logic.

**b. Design changes**
Yes. After reviewing the class skeleton, I made two targeted design refinements:
1. I updated `DailyScheduler.__init__` to accept `pets` as optional and default to `owner.pets`. This reduces duplicated source-of-truth issues where the scheduler could receive a pet list that does not match the owner.
2. I added helper stubs `Pet.get_task(task_id)` and `Owner.list_all_tasks()` to make task access patterns explicit. This should reduce repetitive list-scanning logic spread across methods and make later implementation cleaner.
I made these changes to improve relationship consistency and to prevent potential logic bottlenecks as task volume grows.
---
## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**
- My scheduler uses lightweight conflict detection that only flags exact same-time matches (for example, two tasks both at `08:15`) instead of checking minute-level overlap windows.
- This tradeoff is reasonable for the current scenario because it keeps the logic simple, readable, and fast while still warning the user about the most obvious scheduling collisions.

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
