# Cursor PM

AI-native project management that runs in your IDE. No Jira, no dashboards -- just talk to your projects.

Built for founders and developers who manage projects alongside code. Works with [Cursor](https://cursor.sh) IDE and [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview).

## Why Cursor PM

| Traditional PM | Cursor PM |
|---|---|
| Switch to Jira, create ticket, fill 15 fields | Say "new task: fix auth bug, hot priority" |
| Open dashboard to check progress | Ask "what's today?" |
| Export to spreadsheet to analyze | Ask "how many hours on this project?" |
| Pay $10-50/user/month | Free, runs locally |
| Data locked in vendor | Your data, your CSV files, your git |
| Learn complex UI | Just talk to AI |

## What You Get

- **Projects with goals** -- track initiatives from idea to completion
- **Hierarchical tasks** -- epics, stories, tasks, subtasks with unlimited nesting
- **Task dependencies** -- blocked_by / blocking chains
- **Auto priority scoring** -- algorithm ranks what to work on next
- **Execution logging** -- track time and AI token usage per session
- **Learning capture** -- record insights to improve over time
- **Weekly reports** -- automated summaries of progress
- **CRM integration** -- optional link to [cursor-crm](https://github.com/anthroos/cursor-crm)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/anthroos/cursor-pm.git
cd cursor-pm

# 2. Install dependencies
pip3 install pandas

# 3. Open in your IDE
cursor .  # or claude in terminal

# 4. Start talking
# "New project: Launch MVP"
# "Add task: Design landing page"
# "What's today?"
```

Edit `.cursorrules` to set your name and preferences.

## Project Structure

```
cursor-pm/
├── .cursorrules              # AI rules and skills
├── README.md
│
├── pm/                       # Your data (empty, ready to use)
│   ├── pm_projects_master.csv
│   ├── pm_tasks_master.csv
│   ├── pm_execution_log.csv
│   └── pm_learnings.csv
│
├── sample/                   # Example data to see how it works
│   ├── pm_projects_master.csv
│   ├── pm_tasks_master.csv
│   ├── pm_execution_log.csv
│   └── pm_learnings.csv
│
├── docs/
│   ├── SCHEMA.md             # Field definitions
│   ├── WORKFLOW.md           # Daily/weekly workflow
│   └── PM_FLOW_DIAGRAM.md   # System diagram
│
├── integrations/
│   └── cursor-crm.md        # How to connect with CRM
│
└── scripts/
    ├── validate_pm.py        # Data validation
    ├── calculate_priority.py # Priority score calculator
    └── weekly_report.py      # Weekly summary generator
```

## Key Concepts

### Task Hierarchy

Organize work at any depth:

```
Project: "Launch MVP"
├── Epic: "Backend API"
│   ├── Task: "Design database schema"
│   ├── Task: "Build auth endpoints"
│   │   └── Subtask: "Add OAuth provider"
│   └── Task: "Write API tests"
├── Epic: "Frontend"
│   ├── Task: "Setup React project"
│   └── Task: "Build login page"
```

Each task has a `parent_task_id` linking it to its parent. Top-level tasks have this field empty.

### Task Dependencies

Tasks can block each other:

```
"Design database schema" (task-001)
    └── blocks → "Build auth endpoints" (task-002, blocked_by: task-001)
        └── blocks → "Write API tests" (task-003, blocked_by: task-002)
```

The priority algorithm boosts tasks that block others -- unblocking work is always high priority.

### Priority Scoring

Every task gets an auto-calculated `priority_score` (0.0 to 1.0):

```
priority_score = (
    0.30 * deadline_urgency +     # Closer deadline = higher score
    0.30 * manual_priority +      # hot=1.0, medium=0.5, low=0.2
    0.20 * blocker_impact +       # More tasks blocked = higher
    0.20 * age_factor             # Older unfinished tasks get a boost
)
```

Run the calculator:
```bash
python3 scripts/calculate_priority.py           # Update scores
python3 scripts/calculate_priority.py --dry-run  # Preview without saving
```

### Execution Logging

Track every work session:

```
Session: "Built auth endpoints"
  Duration: 45 minutes
  Tokens: 12,000 in / 8,000 out = 20,000 total
  Type: coding
  Result: completed
  Learning: "OAuth setup takes longer than expected"
```

This data powers weekly reports and helps estimate future tasks.

### Learning Loop

Capture insights as you work:

```
[estimation] "API endpoints take 2x longer when auth is involved"
[technical]  "Use connection pooling for database queries > 100ms"
[process]    "Breaking tasks into < 2hr chunks improves completion rate"
```

Learnings accumulate and become a knowledge base for better planning.

## Common Commands

### Projects

| Say this | What happens |
|----------|-------------|
| "New project: Launch MVP" | Creates project with initial task breakdown |
| "Show projects" | Lists all active projects with progress |
| "Project status: Launch MVP" | Detailed view with task tree |
| "Close project: Launch MVP" | Marks project as completed |

### Tasks

| Say this | What happens |
|----------|-------------|
| "Add task: Build auth" | Adds task to current project |
| "Subtask: Add OAuth" | Adds subtask to current task |
| "Start working on auth" | Sets status to in_progress, notes start time |
| "Done" | Completes task, creates execution log |
| "Blocked by task-002" | Marks task as blocked, updates dependency |
| "Show tasks" | Lists tasks sorted by priority score |

### Tracking

| Say this | What happens |
|----------|-------------|
| "What's today?" | Today's priorities, deadlines, in-progress tasks |
| "Weekly report" | Summary of time, tokens, completed tasks |
| "How much time on Launch MVP?" | Project time and token totals |
| "Show learnings" | All captured insights |
| "Update priorities" | Recalculates priority scores |

## Scripts

```bash
# Validate all PM data
python3 scripts/validate_pm.py

# Calculate priority scores
python3 scripts/calculate_priority.py
python3 scripts/calculate_priority.py --dry-run

# Generate weekly report
python3 scripts/weekly_report.py
```

## Integration with cursor-crm

Cursor PM works great standalone, but if you also do sales/outreach, pair it with [cursor-crm](https://github.com/anthroos/cursor-crm).

When connected:
- Link projects to CRM companies/deals
- Link tasks to specific contacts or outreach activities
- Daily briefing includes both PM tasks and CRM follow-ups
- Priority scoring can factor in CRM recency

See [integrations/cursor-crm.md](integrations/cursor-crm.md) for setup guide.

## Requirements

- [Cursor IDE](https://cursor.sh) (free or pro) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)
- Python 3.10+
- pandas (`pip3 install pandas`)

## Philosophy

1. **Your data stays yours** -- CSV files, version controlled, no vendor lock-in
2. **AI does the work** -- create projects, track tasks, generate reports
3. **Simple beats complex** -- if you need Jira, this isn't for you
4. **Learn from your work** -- execution logs and learnings compound over time
5. **Integrate, don't replace** -- works alongside your existing tools

## Who This Is For

- Solo founders managing multiple projects
- Developers who live in their IDE
- Small teams (1-5) without dedicated project managers
- Anyone tired of context-switching to project management tools

## Who This Is NOT For

- Enterprise teams needing Gantt charts and resource planning
- Organizations requiring audit trails and compliance
- Teams that need real-time collaboration dashboards

## Sample Data

Check the `sample/` directory for pre-filled example data showing a realistic project setup with hierarchy, dependencies, execution logs, and learnings.

## Contributing

PRs welcome. Keep it simple.

## License

MIT

## Credits

Built by [@anthroos](https://github.com/anthroos) at [WeLabelData](https://welabeldata.com).
