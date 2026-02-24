#!/usr/bin/env python3
"""
PM Module Validation Script
Validates all PM CSV files for data integrity.
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

PM_DIR = Path(__file__).parent.parent / "pm"

def load_csv(filename):
    """Load CSV file, return empty DataFrame if file is empty or only has headers."""
    path = PM_DIR / filename
    try:
        df = pd.read_csv(path)
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame()

def validate_projects(df):
    """Validate pm_projects_master.csv"""
    errors = []

    if df.empty:
        return errors

    # Required fields
    required = ['project_id', 'project_name', 'status', 'priority', 'created_date', 'last_updated']
    for field in required:
        if field not in df.columns:
            errors.append(f"Projects: Missing column '{field}'")
            continue
        missing = df[df[field].isna() | (df[field] == '')]
        if not missing.empty:
            errors.append(f"Projects: Missing {field} in {len(missing)} rows")

    # Valid status values
    valid_statuses = ['idea', 'planning', 'in_progress', 'on_hold', 'completed', 'cancelled']
    if 'status' in df.columns:
        invalid = df[~df['status'].isin(valid_statuses)]
        if not invalid.empty:
            errors.append(f"Projects: Invalid status in {len(invalid)} rows")

    # Valid priority values
    valid_priorities = ['hot', 'medium', 'low']
    if 'priority' in df.columns:
        invalid = df[~df['priority'].isin(valid_priorities)]
        if not invalid.empty:
            errors.append(f"Projects: Invalid priority in {len(invalid)} rows")

    # Unique project_id
    if 'project_id' in df.columns:
        duplicates = df[df['project_id'].duplicated()]
        if not duplicates.empty:
            errors.append(f"Projects: Duplicate project_id in {len(duplicates)} rows")

    return errors

def validate_tasks(df, projects_df):
    """Validate pm_tasks_master.csv"""
    errors = []

    if df.empty:
        return errors

    # Required fields
    required = ['task_id', 'project_id', 'task_name', 'status', 'priority', 'created_date', 'last_updated']
    for field in required:
        if field not in df.columns:
            errors.append(f"Tasks: Missing column '{field}'")
            continue
        missing = df[df[field].isna() | (df[field] == '')]
        if not missing.empty:
            errors.append(f"Tasks: Missing {field} in {len(missing)} rows")

    # Valid status values
    valid_statuses = ['backlog', 'todo', 'in_progress', 'blocked', 'review', 'done', 'cancelled']
    if 'status' in df.columns:
        invalid = df[~df['status'].isin(valid_statuses)]
        if not invalid.empty:
            errors.append(f"Tasks: Invalid status in {len(invalid)} rows")

    # FK: project_id must exist
    if 'project_id' in df.columns and not projects_df.empty and 'project_id' in projects_df.columns:
        valid_projects = set(projects_df['project_id'].dropna())
        invalid = df[~df['project_id'].isin(valid_projects)]
        if not invalid.empty:
            errors.append(f"Tasks: Invalid project_id in {len(invalid)} rows")

    # FK: parent_task_id must exist if set
    if 'parent_task_id' in df.columns and 'task_id' in df.columns:
        valid_tasks = set(df['task_id'].dropna())
        has_parent = df[df['parent_task_id'].notna() & (df['parent_task_id'] != '')]
        invalid = has_parent[~has_parent['parent_task_id'].isin(valid_tasks)]
        if not invalid.empty:
            errors.append(f"Tasks: Invalid parent_task_id in {len(invalid)} rows")

    # Check for circular parent references (basic check)
    if 'parent_task_id' in df.columns and 'task_id' in df.columns:
        self_refs = df[df['task_id'] == df['parent_task_id']]
        if not self_refs.empty:
            errors.append(f"Tasks: Self-referencing parent_task_id in {len(self_refs)} rows")

    # Unique task_id
    if 'task_id' in df.columns:
        duplicates = df[df['task_id'].duplicated()]
        if not duplicates.empty:
            errors.append(f"Tasks: Duplicate task_id in {len(duplicates)} rows")

    return errors

def validate_execution_log(df, tasks_df, projects_df):
    """Validate pm_execution_log.csv"""
    errors = []

    if df.empty:
        return errors

    # Required fields
    required = ['log_id', 'task_id', 'project_id', 'date', 'duration_minutes', 'activity_type', 'description', 'result']
    for field in required:
        if field not in df.columns:
            errors.append(f"Execution Log: Missing column '{field}'")
            continue
        missing = df[df[field].isna() | (df[field] == '')]
        if not missing.empty:
            errors.append(f"Execution Log: Missing {field} in {len(missing)} rows")

    # Valid activity_type values
    valid_types = ['planning', 'coding', 'debugging', 'research', 'review', 'discussion', 'other']
    if 'activity_type' in df.columns:
        invalid = df[~df['activity_type'].isin(valid_types)]
        if not invalid.empty:
            errors.append(f"Execution Log: Invalid activity_type in {len(invalid)} rows")

    # Valid result values
    valid_results = ['completed', 'partial', 'blocked', 'failed']
    if 'result' in df.columns:
        invalid = df[~df['result'].isin(valid_results)]
        if not invalid.empty:
            errors.append(f"Execution Log: Invalid result in {len(invalid)} rows")

    # FK: task_id must exist
    if 'task_id' in df.columns and not tasks_df.empty and 'task_id' in tasks_df.columns:
        valid_tasks = set(tasks_df['task_id'].dropna())
        invalid = df[~df['task_id'].isin(valid_tasks)]
        if not invalid.empty:
            errors.append(f"Execution Log: Invalid task_id in {len(invalid)} rows")

    # Unique log_id
    if 'log_id' in df.columns:
        duplicates = df[df['log_id'].duplicated()]
        if not duplicates.empty:
            errors.append(f"Execution Log: Duplicate log_id in {len(duplicates)} rows")

    return errors

def validate_learnings(df):
    """Validate pm_learnings.csv"""
    errors = []

    if df.empty:
        return errors

    # Required fields
    required = ['learning_id', 'type', 'insight', 'created_date']
    for field in required:
        if field not in df.columns:
            errors.append(f"Learnings: Missing column '{field}'")
            continue
        missing = df[df[field].isna() | (df[field] == '')]
        if not missing.empty:
            errors.append(f"Learnings: Missing {field} in {len(missing)} rows")

    # Valid type values
    valid_types = ['estimation', 'process', 'technical', 'tool', 'communication']
    if 'type' in df.columns:
        invalid = df[~df['type'].isin(valid_types)]
        if not invalid.empty:
            errors.append(f"Learnings: Invalid type in {len(invalid)} rows")

    # Unique learning_id
    if 'learning_id' in df.columns:
        duplicates = df[df['learning_id'].duplicated()]
        if not duplicates.empty:
            errors.append(f"Learnings: Duplicate learning_id in {len(duplicates)} rows")

    return errors

def main():
    print("🔍 Validating PM Module Data...")
    print(f"   Directory: {PM_DIR}")
    print()

    # Load all CSVs
    projects_df = load_csv('pm_projects_master.csv')
    tasks_df = load_csv('pm_tasks_master.csv')
    execution_df = load_csv('pm_execution_log.csv')
    learnings_df = load_csv('pm_learnings.csv')

    # Run validations
    all_errors = []
    all_errors.extend(validate_projects(projects_df))
    all_errors.extend(validate_tasks(tasks_df, projects_df))
    all_errors.extend(validate_execution_log(execution_df, tasks_df, projects_df))
    all_errors.extend(validate_learnings(learnings_df))

    # Report results
    if all_errors:
        print("❌ Validation Errors:")
        for error in all_errors:
            print(f"   - {error}")
        sys.exit(1)
    else:
        print("✅ All validations passed!")
        print()
        print("📊 Summary:")
        print(f"   Projects: {len(projects_df)} records")
        print(f"   Tasks: {len(tasks_df)} records")
        print(f"   Execution Logs: {len(execution_df)} records")
        print(f"   Learnings: {len(learnings_df)} records")
        sys.exit(0)

if __name__ == "__main__":
    main()
