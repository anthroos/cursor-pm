# PM System Flow Diagram

## Overview

```mermaid
flowchart LR
    subgraph PLAN["1. Planning"]
        P1[New Idea] --> P2[Create Project]
        P2 --> P3[Break into Tasks]
        P3 --> P4[Set Dependencies]
    end

    subgraph EXEC["2. Execution"]
        E1[Pick by Priority Score] --> E2[Start Task]
        E2 --> E3[Do the Work]
        E3 --> E4[Log Time & Tokens]
        E4 --> E5{Result?}
        E5 -->|completed| E6[Mark Done]
        E5 -->|blocked| E7[Mark Blocked]
        E5 -->|partial| E3
    end

    subgraph TRACK["3. Tracking"]
        T1[Daily: What's Today?]
        T2[Weekly: Review & Report]
        T3[Priority Recalculation]
    end

    subgraph LEARN["4. Learning"]
        L1[Capture Insight]
        L2[Review Estimates vs Actuals]
        L3[Improve Future Planning]
    end

    PLAN --> EXEC
    EXEC --> TRACK
    EXEC --> LEARN
    LEARN --> PLAN
    TRACK --> EXEC
    E6 --> T3
```

---

## Detailed Flows

### Planning Phase

```mermaid
flowchart TD
    A[User: New project idea] --> B{Clarify scope}
    B --> C[Create project in pm_projects_master.csv]
    C --> D[Break into epics/stories/tasks]
    D --> E[Set parent_task_id for hierarchy]
    E --> F[Identify dependencies]
    F --> G[Set blocked_by / blocking]
    G --> H[Assign priorities]
    H --> I[Calculate priority_score]
    I --> J[Ready to execute]
```

### Execution Phase

```mermaid
flowchart TD
    A[Pick highest priority_score task] --> B[Update status: in_progress]
    B --> C[Note start_time]
    C --> D[Execute work]
    D --> E[Note end_time]
    E --> F[Create execution log entry]
    F --> G{Task complete?}
    G -->|Yes| H[Update status: done]
    G -->|Blocked| I[Update status: blocked]
    G -->|Partial| J[Keep in_progress]
    H --> K[Update actual_hours on task & project]
    K --> L[Check: does this unblock other tasks?]
    L --> M[Suggest next task by priority_score]
    I --> N[Record blocker in notes]
```

### Priority Calculation

```
priority_score (0.0 to 1.0) =
    0.30 * deadline_urgency     +    # max(0, 1 - days_until / 14)
    0.30 * manual_priority      +    # hot=1.0, medium=0.5, low=0.2
    0.20 * blocker_impact       +    # min(1, blocking_count * 0.2)
    0.20 * age_factor                # min(0.3, age_days * 0.01)
```

### Weekly Review Flow

```mermaid
flowchart TD
    A[Run weekly_report.py] --> B[Aggregate execution logs]
    B --> C[Count completed tasks]
    C --> D[Calculate time & tokens per project]
    D --> E[Review blocked tasks]
    E --> F[Review captured learnings]
    F --> G[Identify upcoming deadlines]
    G --> H[Recalculate priority scores]
    H --> I[Plan next week priorities]
```

---

## Data Flow Map

```
pm/
├── pm_projects_master.csv    ← Projects registry
│       ↕ project_id
├── pm_tasks_master.csv       ← Tasks with hierarchy & deps
│       ↕ task_id
├── pm_execution_log.csv      ← Time & token tracking
│
└── pm_learnings.csv          ← Captured insights
```

**Key relationships:**
- Tasks belong to Projects (via `project_id`)
- Tasks can nest (via `parent_task_id`)
- Tasks can depend on each other (via `blocked_by` / `blocking`)
- Execution logs link to Tasks and Projects
- Learnings optionally link to Tasks and Projects

---

## Optional: CRM Integration

```mermaid
flowchart LR
    subgraph PM["Plaintext PM"]
        P[Projects]
        T[Tasks]
    end

    subgraph CRM["Plaintext CRM"]
        CO[Companies]
        PE[People]
        AC[Activities]
    end

    P -->|crm_link_type + crm_link_id| CO
    T -->|crm_activity_id| AC
    T -->|crm_person_linkedin_url| PE
```

When plaintext-crm is connected, PM tasks gain CRM context:
- See company info when working on client projects
- See person details when tasks involve specific contacts
- Daily briefing combines PM tasks and CRM follow-ups

See [integrations/plaintext-crm.md](../integrations/plaintext-crm.md) for setup.
