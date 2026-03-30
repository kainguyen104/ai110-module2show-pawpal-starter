# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
My initial UML design separated domain data from planning behavior, which made the system easier to evolve:
- TaskCategory standardizes allowed task categories.
- Task models one care item with duration, priority, time, frequency, due date, and completion state.
- Pet owns and manages its tasks.
- Owner owns pets and stores planning constraints and preferences.
- Scheduler coordinates retrieval, ranking, filtering, scheduling, and explanation.

Responsibility split:
- Domain layer: Task, Pet, and Owner handle data integrity and basic operations.
- Orchestration layer: Scheduler handles planning workflow and decision traceability.

**b. Design changes**
The final implementation evolved beyond the original skeleton in several meaningful ways:
1. Scheduler now defaults to owner.pets to keep a single source of truth for ownership relationships.
2. Task gained is_due_today and score_for_schedule, so due-date logic and scoring are encapsulated in the task model.
3. Scheduler added sort_by_time, detect_time_conflicts, and filter_tasks for practical exploration features in the UI.
4. Scheduler added mark_task_complete and recurring rollover logic for daily and weekly task continuity.
5. get_plan_summary was added to provide a clean API payload for Streamlit display.
6. The class name alias DailyScheduler = Scheduler was retained for backward compatibility.

These changes improved cohesion, reduced duplicated logic in the UI, and made the domain model closer to real usage.
---
## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers:
- Daily time budget (owner.daily_time_available_minutes)
- Task priority
- Task duration
- Due-date/recurrence eligibility for today
- Optional owner preferences (priority weight, duration penalty, category boosts)
- Exact-time collisions for warnings

I prioritized constraints by practical impact:
1. Eligibility (is the task due now?)
2. Value (priority and preference-adjusted score)
3. Feasibility (fits remaining available minutes)

This ordering ensures we do not rank tasks that are not due, and we do not plan tasks that cannot fit in the time budget.

**b. Tradeoffs**
- I intentionally used exact-time conflict warnings instead of full overlap-window math. This keeps the system readable and fast for a first production-quality iteration.
- I used a greedy planner (rank then fill until time runs out) instead of optimization algorithms like knapsack or mixed-integer programming. Greedy planning is easy to explain and test, which matched project scope.
- I allowed flexible owner preferences but kept defaults simple, so behavior is useful immediately without requiring advanced configuration.

---

## 3. AI Collaboration

**a. How you used AI**
I used VS Code Copilot in three modes:
- Design mode: turning UML intent into clean class/method boundaries.
- Implementation mode: generating small method drafts and edge-case checks.
- Verification mode: aligning tests with expected scheduler behavior.

Most effective Copilot features for this scheduler:
- Context-aware chat against the active codebase to reason about interactions between Owner, Pet, Task, and Scheduler.
- Inline completions for repetitive dataclass and list-processing patterns.
- Rapid refactor suggestions while preserving method signatures used by the UI.

Prompts that helped most were specific and bounded, for example:
- "Given this Scheduler API, what methods belong in Task vs Scheduler?"
- "Propose tests for recurrence rollover and conflict detection edge cases."
- "Does my UML still match the final implementation relationships?"

**b. Judgment and verification**
One AI suggestion I rejected was to push too much filtering and formatting logic into the Streamlit layer. I modified that direction and kept filtering and scheduling behavior in Scheduler to preserve clean separation of concerns.

I verified AI suggestions by:
- Checking if behavior fit existing class responsibilities.
- Running and extending tests for sorting, recurrence, and conflict logic.
- Validating that the UI consumed summaries without duplicating domain logic.

How separate chat sessions helped organization:
- Phase 1 session: UML and architecture choices.
- Phase 2 session: implementation and tests.
- Phase 3 session: documentation, README polish, and reflection.

This separation reduced context drift and made each session goal-focused.

---

## 4. Testing and Verification

**a. What you tested**

I tested:
- Task completion updates status correctly.
- Adding a task increases a pet's task list.
- Time sorting returns chronological order.
- Marking daily recurring tasks complete creates the next-day pending task.
- Exact-time conflicts generate warning output.

These tests are important because they target the highest-risk scheduling behaviors: ordering correctness, state transitions, and recurrence continuity.

**b. Confidence**

Confidence level: 4/5.

I am confident in core workflow correctness, but I would add more edge-case coverage next:
- Overlapping (not just exact match) time conflicts.
- Invalid time strings entered by users.
- Preference tuning impacts on ranking stability.
- Larger multi-pet datasets for performance and deterministic ordering.
- UI integration tests for form-driven task creation and schedule generation.

---

## 5. Reflection

**a. What went well**

The strongest part of this project is the separation between domain logic and UI. Streamlit stays focused on interaction, while Scheduler provides reusable planning logic and explanation output.

**b. What you would improve**

In another iteration, I would add:
- True overlap-based conflict detection.
- Optional optimization mode for better global time allocation.
- Edit and complete-task controls directly in the UI with richer history/audit trails.

**c. Key takeaway**

My main takeaway is that AI accelerates implementation, but I still need to act as the lead architect. The human role is to define boundaries, evaluate tradeoffs, reject suggestions that increase coupling, and verify behavior with tests. AI is most effective when guided by clear design intent and disciplined validation.
