#!/usr/bin/env python3
"""
PM Module Validation Script
Validates all PM CSV files for data integrity.
"""

import argparse
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime


def get_pm_dir():
    """Parse --dir argument and return the PM data directory path."""
    parser = argparse.ArgumentParser(description="Validate PM CSV data files.")
    parser.add_argument(
        '--dir',
        default='pm',
        help="Directory containing CSV files (default: pm/)"
    )
    args = parser.parse_args()
    return Path(__file__).parent.parent / args.dir


def load_csv(pm_dir, filename):
    """Load CSV file, return empty DataFrame if file is empty or only has headers."""
    path = pm_dir / filename
    try:
        df = pd.read_csv(path)
        return df
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return pd.DataFrame()


def validate_date_format(df, date_columns, label):
    """Validate that date columns conform to YYYY-MM-DD format."""
    errors = []
    for col in date_columns:
        if col not in df.columns:
            continue
        for idx, value in df[col].items():
            if pd.isna(value) or value == '':
                continue
            try:
                datetime.strptime(str(value), '%Y-%m-%d')
            except ValueError:
                task_id = df.at[idx, 'task_id'] if 'task_id' in df.columns else idx
                errors.append(
                    f"{label}: Invalid date format in '{col}' for {task_id}: '{value}' (expected YYYY-MM-DD)"
                )
    return errors


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

    # Date format validation
    errors.extend(validate_date_format(df, ['created_date', 'last_updated', 'deadline'], 'Projects'))

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

    # Valid priority values
    valid_priorities = ['hot', 'medium', 'low']
    if 'priority' in df.columns:
        invalid = df[~df['priority'].isin(valid_priorities)]
        if not invalid.empty:
            errors.append(f"Tasks: Invalid priority in {len(invalid)} rows")

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

    # FK: blocked_by references must exist
    if 'blocked_by' in df.columns and 'task_id' in df.columns:
        valid_tasks = set(df['task_id'].dropna())
        for idx, row in df.iterrows():
            blocked_by = row.get('blocked_by', '')
            if pd.isna(blocked_by) or blocked_by == '':
                continue
            for ref_id in str(blocked_by).split(','):
                ref_id = ref_id.strip()
                if ref_id and ref_id not in valid_tasks:
                    errors.append(
                        f"Tasks: blocked_by references non-existent task '{ref_id}' in {row['task_id']}"
                    )

    # Check for circular parent references (basic check)
    if 'parent_task_id' in df.columns and 'task_id' in df.columns:
        self_refs = df[df['task_id'] == df['parent_task_id']]
        if not self_refs.empty:
            errors.append(f"Tasks: Self-referencing parent_task_id in {len(self_refs)} rows")

    # Circular dependency detection (blocked_by and parent_task_id)
    errors.extend(_detect_circular_dependencies(df))

    # Unique task_id
    if 'task_id' in df.columns:
        duplicates = df[df['task_id'].duplicated()]
        if not duplicates.empty:
            errors.append(f"Tasks: Duplicate task_id in {len(duplicates)} rows")

    # Blocking/blocked_by bidirectional consistency
    errors.extend(_validate_blocking_consistency(df))

    # Date format validation
    errors.extend(validate_date_format(df, ['created_date', 'last_updated', 'deadline'], 'Tasks'))

    return errors


def _detect_circular_dependencies(df):
    """Detect circular chains in blocked_by and parent_task_id relationships."""
    errors = []

    if 'task_id' not in df.columns:
        return errors

    # Check circular blocked_by chains
    if 'blocked_by' in df.columns:
        # Build adjacency: task -> list of tasks it depends on
        dep_graph = {}
        for _, row in df.iterrows():
            task_id = row['task_id']
            blocked_by = row.get('blocked_by', '')
            if pd.isna(blocked_by) or blocked_by == '':
                dep_graph[task_id] = []
            else:
                dep_graph[task_id] = [b.strip() for b in str(blocked_by).split(',') if b.strip()]

        cycles = _find_cycles(dep_graph)
        for cycle in cycles:
            errors.append(f"Tasks: Circular blocked_by dependency: {' -> '.join(cycle)}")

    # Check circular parent_task_id chains
    if 'parent_task_id' in df.columns:
        parent_graph = {}
        for _, row in df.iterrows():
            task_id = row['task_id']
            parent = row.get('parent_task_id', '')
            if pd.isna(parent) or parent == '':
                parent_graph[task_id] = []
            else:
                parent_graph[task_id] = [str(parent)]

        cycles = _find_cycles(parent_graph)
        for cycle in cycles:
            errors.append(f"Tasks: Circular parent_task_id chain: {' -> '.join(cycle)}")

    return errors


def _find_cycles(graph):
    """Find all cycles in a directed graph using DFS. Returns list of cycle paths."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    path = []
    cycles = []

    def dfs(node):
        color[node] = GRAY
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in color:
                continue
            if color[neighbor] == GRAY:
                # Found cycle: extract the cycle from path
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
            elif color[neighbor] == WHITE:
                dfs(neighbor)
        path.pop()
        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            dfs(node)

    return cycles


def _validate_blocking_consistency(df):
    """Check that blocking/blocked_by fields are bidirectionally consistent."""
    errors = []

    if 'task_id' not in df.columns:
        return errors

    has_blocking = 'blocking' in df.columns
    has_blocked_by = 'blocked_by' in df.columns

    if not has_blocking or not has_blocked_by:
        return errors

    # Build maps: task -> set of tasks it blocks, task -> set of tasks that block it
    blocking_map = {}  # task_id -> set of task_ids it claims to block
    blocked_by_map = {}  # task_id -> set of task_ids that block it

    for _, row in df.iterrows():
        task_id = row['task_id']

        blocking = row.get('blocking', '')
        if pd.notna(blocking) and blocking != '':
            blocking_map[task_id] = {b.strip() for b in str(blocking).split(',') if b.strip()}
        else:
            blocking_map[task_id] = set()

        blocked_by = row.get('blocked_by', '')
        if pd.notna(blocked_by) and blocked_by != '':
            blocked_by_map[task_id] = {b.strip() for b in str(blocked_by).split(',') if b.strip()}
        else:
            blocked_by_map[task_id] = set()

    # If A lists B in blocking, then B should list A in blocked_by
    for task_id, blocks in blocking_map.items():
        for blocked_task in blocks:
            if blocked_task in blocked_by_map:
                if task_id not in blocked_by_map[blocked_task]:
                    errors.append(
                        f"Tasks: {task_id} lists {blocked_task} in 'blocking', "
                        f"but {blocked_task} does not list {task_id} in 'blocked_by'"
                    )

    # If A lists B in blocked_by, then B should list A in blocking
    for task_id, blockers in blocked_by_map.items():
        for blocker_task in blockers:
            if blocker_task in blocking_map:
                if task_id not in blocking_map[blocker_task]:
                    errors.append(
                        f"Tasks: {task_id} lists {blocker_task} in 'blocked_by', "
                        f"but {blocker_task} does not list {task_id} in 'blocking'"
                    )

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

    # Date format validation
    errors.extend(validate_date_format(df, ['date'], 'Execution Log'))

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

    # Date format validation
    errors.extend(validate_date_format(df, ['created_date', 'last_validated'], 'Learnings'))

    return errors


def validate_csv_injection(dataframes):
    """Check all text fields in all CSVs for CSV formula injection.

    Values starting with =, +, -, @, \\t, or \\r can trigger formula execution
    when opened in spreadsheet applications.
    """
    errors = []
    dangerous_prefixes = ('=', '+', '-', '@', '\t', '\r')

    for csv_name, df in dataframes.items():
        if df.empty:
            continue
        for col in df.columns:
            if df[col].dtype != object:
                continue
            for idx, value in df[col].items():
                if not isinstance(value, str):
                    continue
                if value.startswith(dangerous_prefixes):
                    errors.append(
                        f"{csv_name}: Potential CSV injection in column '{col}', "
                        f"row {idx} — value starts with '{value[0]}'"
                    )

    return errors


def main():
    pm_dir = get_pm_dir()

    print("🔍 Validating PM Module Data...")
    print(f"   Directory: {pm_dir}")
    print()

    # Load all CSVs
    projects_df = load_csv(pm_dir, 'pm_projects_master.csv')
    tasks_df = load_csv(pm_dir, 'pm_tasks_master.csv')
    execution_df = load_csv(pm_dir, 'pm_execution_log.csv')
    learnings_df = load_csv(pm_dir, 'pm_learnings.csv')

    # Run validations
    all_errors = []
    all_errors.extend(validate_projects(projects_df))
    all_errors.extend(validate_tasks(tasks_df, projects_df))
    all_errors.extend(validate_execution_log(execution_df, tasks_df, projects_df))
    all_errors.extend(validate_learnings(learnings_df))

    # CSV formula injection check across all files
    all_errors.extend(validate_csv_injection({
        'Projects': projects_df,
        'Tasks': tasks_df,
        'Execution Log': execution_df,
        'Learnings': learnings_df,
    }))

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
