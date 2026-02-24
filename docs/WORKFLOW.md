# Cursor PM - Workflow Guide

## Overview

How to use Cursor PM with Cursor IDE or Claude Code for project and task management.

---

## Core Workflow

### 1. Start New Project

When you have a new idea or initiative:

```
User: "Хочу зробити [опис ідеї]"
Claude:
1. Обговорюємо ідею, уточнюємо деталі
2. Створюю проект в pm_projects_master.csv
3. Розбиваємо на задачі в pm_tasks_master.csv
4. Визначаємо пріоритети та залежності
```

**Project fields to fill:**
- `project_name`: Коротка назва
- `description`: Повний опис
- `goal`: Що означає "зроблено"
- `status`: `planning`
- `priority`: `hot` / `medium` / `low`
- `deadline`: Якщо є

---

### 2. Break Down into Tasks

For each project, create tasks with hierarchy:

```
Epic (parent_task_id = null)
├── Story (parent_task_id = epic_id)
│   ├── Task (parent_task_id = story_id)
│   │   └── Subtask (parent_task_id = task_id)
```

**Example:**
```
Project: "Запустити курс з AI"
├── Epic: "Підготовка контенту"
│   ├── Story: "Модуль 1 - Вступ"
│   │   ├── Task: "Написати скрипт уроку 1"
│   │   ├── Task: "Записати відео уроку 1"
│   │   └── Task: "Створити квіз"
│   └── Story: "Модуль 2 - Практика"
├── Epic: "Маркетинг"
│   ├── Task: "Написати всім про курс" (crm_activity_id linked)
│   ├── Task: "Відтрекати відповіді" (blocked_by = previous)
│   └── Task: "Написати партнерам"
```

---

### 3. Execute Tasks

When starting work on a task:

```
User: "Давай працювати над [task_name]"
Claude:
1. Оновлюю task status → in_progress
2. Виконуємо роботу
3. По завершенню:
   - Оновлюю task status → done
   - Створюю запис в pm_execution_log.csv
   - Вношу час та токени
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
User: "Що в мене на сьогодні?"
Claude:
1. Показую задачі з deadline = today
2. Показую in_progress задачі
3. Показую hot priority задачі
4. Пропоную порядок виконання за priority_score
```

**Weekly review:**
```
User: "Покажи статус проектів"
Claude:
1. Summary всіх активних проектів
2. Витрачений час / токени
3. Blocked задачі
4. Пропозиції по пріоритизації
```

---

## Integration with CRM (Optional)

If you use [cursor-crm](https://github.com/anthroos/cursor-crm), you can link PM tasks to CRM entities. See [integrations/cursor-crm.md](../integrations/cursor-crm.md) for full setup guide.

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
User: "Що найважливіше зараз?"
Claude:
1. Sorts by priority_score DESC
2. Shows top 5 tasks with reasons
3. Recommends which to tackle first
```

---

## Commands Reference

### Project Commands

| Command | Description |
|---------|-------------|
| "Новий проект: [name]" | Create new project |
| "Покажи проекти" | List all active projects |
| "Статус проекту [name]" | Show project details & tasks |
| "Закрий проект [name]" | Mark project completed |

### Task Commands

| Command | Description |
|---------|-------------|
| "Додай задачу: [name]" | Add task to current project |
| "Підзадача: [name]" | Add subtask to current task |
| "Покажи задачі" | List tasks by priority |
| "Працюємо над [task]" | Start working, log execution |
| "Готово" | Complete current task, log time |
| "Заблоковано: [reason]" | Mark task as blocked |

### Tracking Commands

| Command | Description |
|---------|-------------|
| "Що на сьогодні?" | Today's tasks & deadlines |
| "Тижневий звіт" | Weekly summary & stats |
| "Скільки витрачено на [project]?" | Time & token usage |
| "Покажи learnings" | Show captured insights |

---

## Best Practices

1. **Always break down** - No task should be > 2 hours estimated
2. **Set deadlines** - Even soft ones help prioritization
3. **Link to CRM** - If using cursor-crm, keep PM and CRM connected for context
4. **Log immediately** - Don't batch execution logs
5. **Capture learnings** - They compound over time
6. **Review weekly** - Adjust priorities, clean up done tasks
