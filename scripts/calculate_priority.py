#!/usr/bin/env python3
"""
Priority Score Calculator
Calculates and updates priority_score for all tasks.

Usage:
    python3 scripts/calculate_priority.py             # Update scores
    python3 scripts/calculate_priority.py --dry-run    # Preview without saving
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

PM_DIR = Path(__file__).parent.parent / "pm"


def calculate_priority_scores(dry_run=False):
    """Calculate priority_score for all tasks."""

    tasks_path = PM_DIR / "pm_tasks_master.csv"
    tasks_df = pd.read_csv(tasks_path)

    if tasks_df.empty:
        print("No tasks to process.")
        return

    today = datetime.now().date()

    # Build blocking count map
    blocking_counts = {}
    if 'blocked_by' in tasks_df.columns:
        for _, row in tasks_df.iterrows():
            blocked_by = row.get('blocked_by', '')
            if pd.notna(blocked_by) and blocked_by:
                for blocker_id in str(blocked_by).split(','):
                    blocker_id = blocker_id.strip()
                    blocking_counts[blocker_id] = blocking_counts.get(blocker_id, 0) + 1

    # Calculate score for each task
    scores = []
    for _, row in tasks_df.iterrows():
        task_id = row.get('task_id', '')

        # Skip completed/cancelled tasks
        status = row.get('status', '')
        if status in ['done', 'cancelled']:
            scores.append(0.0)
            continue

        # 1. Deadline urgency (30%)
        deadline_urgency = 0.0
        deadline = row.get('deadline')
        if pd.notna(deadline) and deadline:
            try:
                deadline_date = datetime.strptime(str(deadline), '%Y-%m-%d').date()
                days_until = (deadline_date - today).days
                deadline_urgency = max(0, min(1, 1 - (days_until / 14)))
            except (ValueError, TypeError):
                pass

        # 2. Manual priority (30%)
        priority = row.get('priority', 'medium')
        priority_map = {'hot': 1.0, 'medium': 0.5, 'low': 0.2}
        manual_priority = priority_map.get(priority, 0.5)

        # 3. Blocker impact (20%)
        blocker_impact = min(1, blocking_counts.get(task_id, 0) * 0.2)

        # 4. Age factor (20%)
        age_factor = 0.0
        created_date = row.get('created_date')
        if pd.notna(created_date) and created_date:
            try:
                created = datetime.strptime(str(created_date), '%Y-%m-%d').date()
                age_days = (today - created).days
                age_factor = min(0.3, age_days * 0.01)
            except (ValueError, TypeError):
                pass

        # Calculate final score
        score = (
            0.30 * deadline_urgency +
            0.30 * manual_priority +
            0.20 * blocker_impact +
            0.20 * age_factor
        )
        scores.append(round(score, 3))

    # Update DataFrame
    tasks_df['priority_score'] = scores
    tasks_df['last_updated'] = today.strftime('%Y-%m-%d')

    if dry_run:
        print("DRY RUN - no changes saved")
        print()
    else:
        tasks_df.to_csv(tasks_path, index=False)
        print("Priority Scores Updated")
        print()

    # Show top 10 by priority
    active_tasks = tasks_df[~tasks_df['status'].isin(['done', 'cancelled'])]
    if not active_tasks.empty:
        top_tasks = active_tasks.nlargest(10, 'priority_score')
        print("Top Priority Tasks:")
        for _, task in top_tasks.iterrows():
            print(f"   [{task['priority_score']:.2f}] [{task['status']}] {task['task_name']}")


def main():
    dry_run = '--dry-run' in sys.argv
    calculate_priority_scores(dry_run=dry_run)


if __name__ == "__main__":
    main()
