#!/usr/bin/env python3
"""
Quick timesheet diagnostic - run this in Odoo shell to check basic data
./odoo-bin shell -d your_database_name --addons-path=/path/to/addons
>>> exec(open('quick_timesheet_check.py').read())
"""

print("=== QUICK TIMESHEET DIAGNOSTIC ===")

# Check if we have any timesheet entries at all
all_timesheets = env['account.analytic.line'].search([])
print(f"Total timesheet entries in system: {len(all_timesheets)}")

if all_timesheets:
    print("\nSample timesheet entries:")
    for i, ts in enumerate(all_timesheets[:5]):  # Show first 5
        emp_name = ts.employee_id.name if ts.employee_id else "NO EMPLOYEE"
        proj_name = ts.project_id.name if ts.project_id else "NO PROJECT"
        print(f"  {i+1}. Date: {ts.date}, Employee: {emp_name}, Project: {proj_name}, Hours: {ts.unit_amount}")

# Check employees
employees = env['hr.employee'].search([])
print(f"\nTotal employees: {len(employees)}")

if employees:
    print("Employees:")
    for emp in employees[:3]:  # Show first 3
        print(f"  - {emp.name} (ID: {emp.id})")

# Check current user's employee
current_user_emp = env.user.employee_id
if current_user_emp:
    print(f"\nCurrent user employee: {current_user_emp.name}")
    
    # Check timesheets for current user
    user_timesheets = env['account.analytic.line'].search([
        ('employee_id', '=', current_user_emp.id)
    ])
    print(f"Timesheets for current user: {len(user_timesheets)}")
    
    if user_timesheets:
        print("Current user's timesheet entries:")
        for ts in user_timesheets[-3:]:  # Show last 3
            proj_name = ts.project_id.name if ts.project_id else "NO PROJECT"
            print(f"  - Date: {ts.date}, Project: {proj_name}, Hours: {ts.unit_amount}, Desc: {ts.name}")
else:
    print("\nNo employee record for current user!")

print("\n=== END DIAGNOSTIC ===")
