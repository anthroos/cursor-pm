# Integration with cursor-crm

## Overview

Cursor PM works standalone. If you also manage sales/outreach, you can connect it to [cursor-crm](https://github.com/anthroos/cursor-crm) for bidirectional context.

**What you get:**
- Link projects to CRM companies and deals
- Link tasks to specific contacts or outreach activities
- Daily briefing includes CRM follow-ups alongside PM tasks
- Priority scoring can factor in CRM recency (advanced)

---

## Setup

### 1. Clone both repos side by side

```
~/work/
├── cursor-crm/     # Sales & CRM data
│   └── sales/crm/
└── cursor-pm/      # Project management
    └── pm/
```

### 2. Enable CRM integration in CLAUDE.md

Open `cursor-pm/CLAUDE.md` and change:

```
CRM_INTEGRATION: true
CRM_PATH: ../cursor-crm/sales/crm
```

This activates CRM-related skills and context lookups.

---

## How Linking Works

### Project-level: crm_link_type + crm_link_id

Link a project to a CRM entity:

```csv
project_name,crm_link_type,crm_link_id
"Acme Corp Partnership",company,acme.com
"John's Onboarding",person,https://linkedin.com/in/john-doe
```

**crm_link_type values:**
- `company` -- link to a company (crm_link_id = company website or company_id)
- `person` -- link to a person (crm_link_id = linkedin_url or person_id)
- `activity` -- link to an outreach activity (crm_link_id = activity_id)

### Task-level: crm_activity_id + crm_person_linkedin_url

Link a task to a specific CRM record:

```csv
task_name,crm_activity_id,crm_person_linkedin_url
"Follow up on demo",act-001,https://linkedin.com/in/john-doe
"Send proposal to Jane",,https://linkedin.com/in/jane-smith
```

---

## Workflow Examples

### Example 1: Client project from a deal

```
CRM: Deal "Acme Corp AI Pilot" won
 ->
PM: Create project "Acme Corp Pilot" (crm_link_type: company, crm_link_id: acme.com)
 ->
PM: Break into tasks:
  - "Kickoff call with John" (crm_person_linkedin_url: linkedin.com/in/john-acme)
  - "Deliver phase 1"
  - "Invoice phase 1"
```

### Example 2: Outreach follow-up as a task

```
CRM: Sent 50 outreach messages (activity logged)
 ->
PM: Create task "Track responses by Wednesday"
    crm_activity_id: act-batch-001
    deadline: 2026-02-26
 ->
Wednesday: "What's today?" shows the task with CRM context
 ->
Execute: Check CRM for replies, update statuses, create follow-up tasks
```

### Example 3: Daily briefing with both systems

```
"What's today?"

=== TODAY: 2026-02-24 ===

DEADLINE TODAY:
  [proj-001] Send invoice to Acme

IN PROGRESS:
  [proj-001] Build auth API

HOT TASKS (top 5):
  [proj-001] Demo for John (score: 0.85)
    CRM: John Smith @ Acme Corp, last contact 2026-02-20

CRM FOLLOW-UPS:
  Jane Doe (Beta Corp) -- follow-up due today
  Mike Lee (Gamma Inc) -- 3 days overdue
```

---

## Advanced: Priority Scoring with CRM Recency

When CRM is connected, you can extend the priority formula from 4 to 5 factors:

```
# Standalone (default)
priority_score = 0.30*deadline + 0.30*priority + 0.20*blocker + 0.20*age

# With CRM (advanced)
priority_score = 0.25*deadline + 0.25*priority + 0.20*blocker + 0.15*age + 0.15*crm_recency
```

Where `crm_recency` = how recently the linked CRM person/company was contacted. Recent contact = higher urgency to follow through.

To enable: update the formula in `scripts/calculate_priority.py`.

---

## Directory Structure (both repos)

```
~/work/
├── cursor-crm/
│   ├── CLAUDE.md
│   ├── sales/
│   │   └── crm/
│   │       ├── contacts/
│   │       │   ├── companies.csv
│   │       │   └── people.csv
│   │       ├── relationships/
│   │       │   ├── leads.csv
│   │       │   ├── clients.csv
│   │       │   ├── partners.csv
│   │       │   └── deals.csv
│   │       ├── activities.csv
│   │       └── products.csv
│   ├── integrations/
│   └── scripts/
│
└── cursor-pm/
    ├── CLAUDE.md
    ├── pm/
    │   ├── pm_projects_master.csv
    │   ├── pm_tasks_master.csv
    │   ├── pm_execution_log.csv
    │   └── pm_learnings.csv
    ├── integrations/
    └── scripts/
```

Both repos are independent git repositories. No shared dependencies. Integration is purely at the data level through shared IDs/URLs.

---

## Skills Framework

For advanced automation (scheduled briefings, multi-channel notifications, agent workflows), see [claude-skills](https://github.com/anthroos/claude-skills). The skills repo provides:
- Scheduled daily briefings combining PM + CRM data
- Multi-channel outreach agents (Telegram, Email, WhatsApp)
- CRM data import and validation pipelines
- Process analysis and automation tools
