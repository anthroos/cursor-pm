# Plaintext PM - Schema Documentation

## Overview

CSV-based project and task management, optimized for Cursor IDE and Claude Code. Tracks projects, tasks (with unlimited hierarchy), execution time/tokens, and learnings.

Works standalone. Optionally integrates with [plaintext-crm](https://github.com/anthroos/plaintext-crm) -- see [integrations/plaintext-crm.md](../integrations/plaintext-crm.md).

---

## Tables

### 1. pm_projects_master.csv

Master table for all projects.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | string | Yes | Unique identifier (format: proj-XXXX) |
| `project_name` | string | Yes | Short project name |
| `description` | string | No | Full project description |
| `goal` | string | No | What success looks like |
| `status` | enum | Yes | `idea` / `planning` / `in_progress` / `on_hold` / `completed` / `cancelled` |
| `priority` | enum | Yes | `hot` / `medium` / `low` |
| `priority_score` | float | No | Auto-calculated 0.0-1.0 (based on deadline, blockers, business value) |
| `owner` | string | No | Responsible person |
| `created_date` | YYYY-MM-DD | Yes | When project was created |
| `last_updated` | YYYY-MM-DD | Yes | Last modification date |
| `deadline` | YYYY-MM-DD | No | Target completion date |
| `estimated_hours` | float | No | Estimated total hours |
| `actual_hours` | float | No | Sum of execution log hours |
| `actual_tokens` | int | No | Sum of execution log tokens |
| `crm_link_type` | enum | No | *Optional CRM integration:* `company` / `person` / `activity` |
| `crm_link_id` | string | No | *Optional CRM integration:* ID/URL from CRM |
| `tags` | string | No | Comma-separated tags |
| `notes` | string | No | Additional notes |

**Primary Key**: `project_id`

---

### 2. pm_tasks_master.csv

Master table for all tasks with unlimited hierarchy support.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | string | Yes | Unique identifier (format: task-XXXX, zero-padded decimal) |
| `project_id` | string | Yes | FK to pm_projects_master |
| `parent_task_id` | string | No | FK to pm_tasks_master (for subtasks) |
| `task_name` | string | Yes | Short task name |
| `description` | string | No | Full task description |
| `status` | enum | Yes | `backlog` / `todo` / `in_progress` / `blocked` / `review` / `done` / `cancelled` |
| `priority` | enum | Yes | `hot` / `medium` / `low` |
| `priority_score` | float | No | Auto-calculated 0.0-1.0 |
| `assignee` | string | No | Who is responsible |
| `created_date` | YYYY-MM-DD | Yes | When task was created |
| `last_updated` | YYYY-MM-DD | Yes | Last modification date |
| `deadline` | YYYY-MM-DD | No | Target completion date |
| `estimated_hours` | float | No | Estimated hours for this task |
| `actual_hours` | float | No | Sum of execution log hours |
| `actual_tokens` | int | No | Sum of execution log tokens |
| `blocked_by` | string | No | Comma-separated task_ids that block this task |
| `blocking` | string | No | Comma-separated task_ids this task is blocking |
| `crm_activity_id` | string | No | *Optional CRM integration:* FK to CRM activities |
| `crm_person_linkedin_url` | string | No | *Optional CRM integration:* FK to CRM people |
| `tags` | string | No | Comma-separated tags |
| `notes` | string | No | Additional notes |
| `order_index` | int | No | For manual ordering within same parent |

**Primary Key**: `task_id`
**Foreign Keys**: `project_id` → pm_projects_master, `parent_task_id` → pm_tasks_master

---

### 3. pm_execution_log.csv

Tracks every work session on a task (time, tokens, results).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `log_id` | string | Yes | Unique identifier |
| `task_id` | string | Yes | FK to pm_tasks_master |
| `project_id` | string | Yes | FK to pm_projects_master (denormalized for queries) |
| `date` | YYYY-MM-DD | Yes | Session date |
| `start_time` | HH:MM | No | When work started |
| `end_time` | HH:MM | No | When work ended |
| `duration_minutes` | int | Yes | Total minutes spent |
| `tokens_input` | int | No | Input tokens used |
| `tokens_output` | int | No | Output tokens used |
| `tokens_total` | int | No | Total tokens (input + output) |
| `activity_type` | enum | Yes | `planning` / `coding` / `debugging` / `research` / `review` / `discussion` / `other` |
| `description` | string | Yes | What was done |
| `result` | enum | Yes | `completed` / `partial` / `blocked` / `failed` |
| `blockers_encountered` | string | No | What blockers were hit |
| `learnings` | string | No | Key insights from this session |
| `claude_session_id` | string | No | Reference to Claude conversation |

**Primary Key**: `log_id`

---

### 4. pm_learnings.csv

Aggregated learnings from project work for continuous improvement.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `learning_id` | string | Yes | Unique identifier |
| `type` | enum | Yes | `estimation` / `process` / `technical` / `tool` / `communication` |
| `project_id` | string | No | Related project (if specific) |
| `task_id` | string | No | Related task (if specific) |
| `insight` | string | Yes | The learning itself |
| `impact_score` | float | No | How impactful (0.0-1.0) |
| `evidence_count` | int | No | How many times observed |
| `tags` | string | No | Comma-separated tags |
| `created_date` | YYYY-MM-DD | Yes | When learning was captured |
| `last_validated` | YYYY-MM-DD | No | When last confirmed still valid |

**Primary Key**: `learning_id`

---

## Priority Score Calculation

Auto-calculated `priority_score` (0.0 to 1.0) based on 4 factors:

```
priority_score = (
    0.30 * deadline_urgency +      # max(0, 1 - days_until / 14)
    0.30 * manual_priority +       # hot=1.0, medium=0.5, low=0.2
    0.20 * blocker_impact +        # min(1, blocking_count * 0.2)
    0.20 * age_factor              # min(0.3, age_days * 0.01)
)
```

Run: `python3 scripts/calculate_priority.py` or add `--dry-run` to preview.

---

## CRM Integration (Optional)

If you use [plaintext-crm](https://github.com/anthroos/plaintext-crm), tasks and projects can be linked to CRM entities:

- **crm_activity_id**: Links task to an outreach activity
- **crm_person_linkedin_url**: Links task to a specific person
- **crm_link_type + crm_link_id** on projects: Links project to a company/person/activity

These fields are empty by default. See [integrations/plaintext-crm.md](../integrations/plaintext-crm.md) for setup.

---

## Validation Rules

1. `project_id` must exist in pm_projects_master before creating tasks
2. `parent_task_id` must exist in pm_tasks_master if set
3. `last_updated` must always be updated on any change
4. `status` transitions should be logical (can't go from `done` to `todo`)
5. `blocked_by` task_ids must all exist
6. Circular dependencies in `blocked_by` / `parent_task_id` are not allowed
