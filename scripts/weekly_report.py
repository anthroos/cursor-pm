#!/usr/bin/env python3
"""
Weekly Report Generator
Generates a summary of work done in the past week.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

PM_DIR = Path(__file__).parent.parent / "pm"

def generate_weekly_report():
    """Generate weekly summary report."""

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    # Load data
    def safe_read(filename):
        path = PM_DIR / filename
        try:
            return pd.read_csv(path)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame()

    projects_df = safe_read("pm_projects_master.csv")
    tasks_df = safe_read("pm_tasks_master.csv")
    execution_df = safe_read("pm_execution_log.csv")
    learnings_df = safe_read("pm_learnings.csv")

    print("=" * 60)
    print(f"📅 WEEKLY REPORT: {week_ago} to {today}")
    print("=" * 60)
    print()

    # Execution stats for the week
    if not execution_df.empty and 'date' in execution_df.columns:
        execution_df['date'] = pd.to_datetime(execution_df['date']).dt.date
        week_logs = execution_df[(execution_df['date'] >= week_ago) & (execution_df['date'] <= today)]

        if not week_logs.empty:
            total_minutes = week_logs['duration_minutes'].sum() if 'duration_minutes' in week_logs.columns else 0
            total_tokens = week_logs['tokens_total'].sum() if 'tokens_total' in week_logs.columns else 0
            sessions = len(week_logs)

            print("⏱️  TIME & TOKENS")
            print(f"   Sessions: {sessions}")
            print(f"   Total time: {total_minutes} minutes ({total_minutes/60:.1f} hours)")
            print(f"   Total tokens: {total_tokens:,}")
            print()

            # By activity type
            if 'activity_type' in week_logs.columns:
                by_type = week_logs.groupby('activity_type').agg({
                    'duration_minutes': 'sum',
                    'log_id': 'count'
                }).rename(columns={'log_id': 'sessions'})

                print("   By activity type:")
                for activity, row in by_type.iterrows():
                    print(f"      {activity}: {row['duration_minutes']} min ({row['sessions']} sessions)")
                print()
    else:
        print("⏱️  TIME & TOKENS")
        print("   No execution logs this week")
        print()

    # Tasks completed this week
    if not tasks_df.empty and 'last_updated' in tasks_df.columns:
        tasks_df['last_updated'] = pd.to_datetime(tasks_df['last_updated']).dt.date
        completed_this_week = tasks_df[
            (tasks_df['status'] == 'done') &
            (tasks_df['last_updated'] >= week_ago)
        ]

        print("✅ TASKS COMPLETED")
        if not completed_this_week.empty:
            print(f"   Total: {len(completed_this_week)}")
            for _, task in completed_this_week.iterrows():
                print(f"   - {task['task_name']}")
        else:
            print("   No tasks completed this week")
        print()

    # Active projects status
    if not projects_df.empty:
        active_projects = projects_df[projects_df['status'].isin(['planning', 'in_progress'])]

        print("📁 ACTIVE PROJECTS")
        if not active_projects.empty:
            for _, proj in active_projects.iterrows():
                project_id = proj['project_id']
                proj_tasks = tasks_df[tasks_df['project_id'] == project_id] if 'project_id' in tasks_df.columns else pd.DataFrame()

                total = len(proj_tasks)
                done = len(proj_tasks[proj_tasks['status'] == 'done']) if not proj_tasks.empty else 0
                in_progress = len(proj_tasks[proj_tasks['status'] == 'in_progress']) if not proj_tasks.empty else 0
                blocked = len(proj_tasks[proj_tasks['status'] == 'blocked']) if not proj_tasks.empty else 0

                progress = (done / total * 100) if total > 0 else 0

                print(f"   {proj['project_name']} [{proj['priority']}]")
                print(f"      Status: {proj['status']}")
                print(f"      Progress: {done}/{total} tasks ({progress:.0f}%)")
                if in_progress > 0:
                    print(f"      In progress: {in_progress}")
                if blocked > 0:
                    print(f"      ⚠️  Blocked: {blocked}")
                print()
        else:
            print("   No active projects")
            print()

    # Blocked tasks
    if not tasks_df.empty:
        blocked_tasks = tasks_df[tasks_df['status'] == 'blocked']
        if not blocked_tasks.empty:
            print("🚧 BLOCKED TASKS")
            for _, task in blocked_tasks.iterrows():
                blocker = task.get('blocked_by', 'Unknown')
                print(f"   - {task['task_name']}")
                print(f"     Blocked by: {blocker}")
            print()

    # Learnings this week
    if not learnings_df.empty and 'created_date' in learnings_df.columns:
        learnings_df['created_date'] = pd.to_datetime(learnings_df['created_date']).dt.date
        week_learnings = learnings_df[learnings_df['created_date'] >= week_ago]

        print("💡 LEARNINGS")
        if not week_learnings.empty:
            for _, learning in week_learnings.iterrows():
                print(f"   [{learning['type']}] {learning['insight']}")
        else:
            print("   No learnings captured this week")
        print()

    # Upcoming deadlines
    if not tasks_df.empty and 'deadline' in tasks_df.columns:
        tasks_df['deadline'] = pd.to_datetime(tasks_df['deadline'], errors='coerce').dt.date
        next_week = today + timedelta(days=7)
        upcoming = tasks_df[
            (tasks_df['deadline'].notna()) &
            (tasks_df['deadline'] <= next_week) &
            (~tasks_df['status'].isin(['done', 'cancelled']))
        ].sort_values('deadline')

        if not upcoming.empty:
            print("📆 UPCOMING DEADLINES (next 7 days)")
            for _, task in upcoming.iterrows():
                days_left = (task['deadline'] - today).days
                urgency = "🔴" if days_left <= 1 else "🟡" if days_left <= 3 else "🟢"
                print(f"   {urgency} {task['deadline']} - {task['task_name']} ({days_left} days)")
            print()

    print("=" * 60)

def main():
    generate_weekly_report()

if __name__ == "__main__":
    main()
