#!/usr/bin/env python3
"""
Debug script to check timesheet entries for troubleshooting
This script should be run in the Odoo shell environment
"""

def debug_timesheet_entries(env, employee_name="Lovaraju Mylapalli", date_from="2025-07-01", date_to="2025-07-31"):
    """
    Debug function to check what timesheet entries exist for an employee
    
    Usage in Odoo shell:
    $ python odoo-bin shell -d your_database_name
    >>> exec(open('debug_timesheet_entries.py').read())
    >>> debug_timesheet_entries(env)
    """
    
    print(f"\n=== DEBUGGING TIMESHEET ENTRIES ===")
    print(f"Employee: {employee_name}")
    print(f"Date Range: {date_from} to {date_to}")
    print("=" * 50)
    
    # Find employee
    employee = env['hr.employee'].search([('name', '=', employee_name)], limit=1)
    if not employee:
        print(f"ERROR: Employee '{employee_name}' not found!")
        print("Available employees:")
        employees = env['hr.employee'].search([])
        for emp in employees[:10]:  # Show first 10
            print(f"  - {emp.name} (ID: {emp.id})")
        return
    
    print(f"Found employee: {employee.name} (ID: {employee.id})")
    
    # Check all timesheet entries
    all_entries = env['account.analytic.line'].search([
        ('employee_id', '=', employee.id),
        ('date', '>=', date_from),
        ('date', '<=', date_to),
    ])
    
    print(f"\nTotal timesheet entries found: {len(all_entries)}")
    
    if not all_entries:
        print("No timesheet entries found at all!")
        print("\nChecking if any timesheet entries exist for this employee...")
        any_entries = env['account.analytic.line'].search([
            ('employee_id', '=', employee.id)
        ], limit=5)
        if any_entries:
            print(f"Found {len(any_entries)} entries for this employee in other periods:")
            for entry in any_entries:
                print(f"  - Date: {entry.date}, Project: {entry.project_id.name if entry.project_id else 'NO PROJECT'}, Hours: {entry.unit_amount}")
        else:
            print("No timesheet entries found for this employee at all!")
        return
    
    # Analyze entries
    entries_with_projects = all_entries.filtered(lambda line: line.project_id)
    entries_without_projects = all_entries.filtered(lambda line: not line.project_id)
    
    print(f"Entries with projects: {len(entries_with_projects)}")
    print(f"Entries without projects: {len(entries_without_projects)}")
    
    print(f"\n=== DETAILED BREAKDOWN ===")
    
    for i, entry in enumerate(all_entries, 1):
        print(f"{i}. Date: {entry.date}")
        print(f"   Project: {entry.project_id.name if entry.project_id else '*** NO PROJECT ***'}")
        print(f"   Task: {entry.task_id.name if entry.task_id else 'No task'}")
        print(f"   Hours: {entry.unit_amount}")
        print(f"   Description: {entry.name[:50] if entry.name else 'No description'}...")
        print(f"   Line ID: {entry.id}")
        print()
    
    print(f"=== SUMMARY ===")
    if entries_with_projects:
        print(f"✓ Found {len(entries_with_projects)} entries with projects - these should appear in submission")
    if entries_without_projects:
        print(f"⚠ Found {len(entries_without_projects)} entries WITHOUT projects - these need 'Include Entries Without Projects' option")
    
    print(f"\n=== RECOMMENDED ACTION ===")
    if entries_with_projects:
        print("You should see timesheet entries in the submission wizard")
    elif entries_without_projects:
        print("Enable 'Include Entries Without Projects' checkbox in the submission wizard")
    else:
        print("Create some timesheet entries first in Timesheets > My Timesheets")

if __name__ == "__main__":
    print("This script should be run in Odoo shell environment")
    print("Usage:")
    print("$ python odoo-bin shell -d your_database_name")
    print(">>> exec(open('debug_timesheet_entries.py').read())")
    print(">>> debug_timesheet_entries(env)")
