# Plaintext PM - Workflow Guide

## Overview

How to use Plaintext PM with Claude Code or Cursor IDE for project and task management.

---

## Core Workflow

### 1. Start New Project

When you have a new idea or initiative:

```
User: "I want to build [idea description]"
AI:
1. Discuss the idea, clarify details
2. Create project in pm_projects_master.csv
3. Break down into tasks in pm_tasks_master.csv
4. Set priorities and dependencies
```

**Project fields to fill:**
- `project_name`: Short name
- `description`: Full description
- `goal`: What "done" looks like
- `status`: `planning`
- `priority`: `hot` / `medium` / `low`
- `deadline`: If applicable

---

### 2. Break Down into Tasks

For each project, create tasks with hierarchy:

```
Epic (parent_task_id = null)
-- Story (parent_task_id = epic_id)
   -- Task (parent_task_id = story_id)
      -- Subtask (parent_task_id = task_id)
```

**Example:**
```
Project: "Launch AI Course"
-- Epic: "Content Preparation"
   -- Story: "Module 1 - Introduction"
      -- Task: "Write lesson 1 script"
      -- Task: "Record lesson 1 video"
      -- Task: "Create quiz"
   -- Story: "Module 2 - Practice"
-- Epic: "Marketing"
   -- Task: "Send outreach about course" (crm_activity_id linked)
   -- Task: "Track responses" (blocked_by = previous)
   -- Task: "Reach out to partners"
```

---

### 3. Execute Tasks

When starting work on a task:

```
User: "Let's work on [task_name]"
AI:
1. Update task status -> in_progress
2. Do the work
3. On completion:
   - Update task status -> done
   - Create entry in pm_execution_log.csv
   - Log time and tokens
```

**Execution log captures:**
- Duration (minutes)
- Tokens used (input/output)
- Activity type (coding, research, etc.)
- Result (completed, partial, blocked)
- Key learnings

---

### 4. Track Progress

**Daily check:**
```
User: "What's on my plate today?"
AI:
1. Show tasks with deadline = today
2. Show in_progress tasks
3. Show hot priority tasks
4. Suggest execution order by priority_score
```

**Weekly review:**
```
User: "Show project status"
AI:
1. Summary of all active projects
2. Time / tokens spent
3. Blocked tasks
4. Prioritization suggestions
```

---

## Integration with CRM (Optional)

If you use [plaintext-crm](https://github.com/anthroos/plaintext-crm), you can link PM tasks to CRM entities. See [integrations/plaintext-crm.md](../integrations/plaintext-crm.md) for full setup guide.

---

## Priority System

### Manual Priority

Set by user:
- `hot`: Needs immediate attention
- `medium`: Important but not urgent
- `low`: Nice to have

### Auto Priority Score

Calculated 0.0-1.0 based on:

| Factor | Weight | Calculation |
|--------|--------|-------------|
| Deadline urgency | 30% | Days until deadline (closer = higher) |
| Manual priority | 30% | hot=1.0, medium=0.5, low=0.2 |
| Blocker impact | 20% | How many tasks this blocks |
| Age | 20% | Older unfinished get boost |

### Using Priority

```
User: "What's most important right now?"
AI:
1. Sorts by priority_score DESC
2. Shows top 5 tasks with reasons
3. Recommends which to tackle first
```

---

## Commands Reference

### Project Commands

| Command | Description |
|---------|-------------|
| "New project: [name]" | Create new project |
| "Show projects" | List all active projects |
| "Project status: [name]" | Show project details & tasks |
| "Close project: [name]" | Mark project completed |

### Task Commands

| Command | Description |
|---------|-------------|
| "Add task: [name]" | Add task to current project |
| "Subtask: [name]" | Add subtask to current task |
| "Show tasks" | List tasks by priority |
| "Work on [task]" | Start working, log execution |
| "Done" | Complete current task, log time |
| "Blocked: [reason]" | Mark task as blocked |

### Tracking Commands

| Command | Description |
|---------|-------------|
| "What's today?" | Today's tasks & deadlines |
| "Weekly report" | Weekly summary & stats |
| "How much spent on [project]?" | Time & token usage |
| "Show learnings" | Show captured insights |

---

## Best Practices

1. **Always break down** - No task should be > 2 hours estimated
2. **Set deadlines** - Even soft ones help prioritization
3. **Link to CRM** - If using plaintext-crm, keep PM and CRM connected for context
4. **Log immediately** - Don't batch execution logs
5. **Capture learnings** - They compound over time
6. **Review weekly** - Adjust priorities, clean up done tasks
