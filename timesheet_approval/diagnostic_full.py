"""
Diagnostic script for timesheet approval issues
Run this in Odoo shell to check timesheet data directly

Usage:
./odoo-bin shell -d your_database_name
>>> exec(open('/path/to/this/script.py').read())
"""

# Get current user and employee
user = env.user
employee = env['hr.employee'].search([('user_id', '=', user.id)], limit=1)

if not employee:
    print("No employee record found for current user")
    employees = env['hr.employee'].search([])
    if employees:
        employee = employees[0]
        print(f"Using first available employee: {employee.name}")
    else:
        print("No employees found in system")
        exit()

print(f"Employee: {employee.name}")
print(f"User: {user.name}")

# Check for timesheet entries
from datetime import datetime, timedelta
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)  # Last 30 days

timesheet_lines = env['account.analytic.line'].search([
    ('employee_id', '=', employee.id),
    ('date', '>=', start_date),
    ('date', '<=', end_date),
])

print(f"\nTimesheet entries for {employee.name} from {start_date} to {end_date}:")
print(f"Found {len(timesheet_lines)} entries")

for line in timesheet_lines:
    project_name = line.project_id.name if line.project_id else "NO PROJECT"
    print(f"  Date: {line.date}, Project: {project_name}, Hours: {line.unit_amount}, Description: {line.name}")

# Check for existing timesheet approvals
approvals = env['timesheet.approval'].search([('employee_id', '=', employee.id)])
print(f"\nExisting timesheet approvals: {len(approvals)}")
for approval in approvals:
    print(f"  ID: {approval.id}, Period: {approval.date_from} to {approval.date_to}, State: {approval.state}")

# Test creating a new approval
if timesheet_lines:
    print("\nTesting timesheet approval creation...")
    try:
        approval = env['timesheet.approval'].create({
            'employee_id': employee.id,
            'date_from': start_date,
            'date_to': end_date,
            'manager_id': employee.parent_id.id if employee.parent_id else employee.id,
        })
        print(f"Created approval: {approval.id}")
        
        # Test loading timesheet lines
        approval._load_timesheet_lines()
        print(f"Loaded {len(approval.timesheet_line_ids)} timesheet lines")
        
        for line in approval.timesheet_line_ids:
            print(f"  Approval Line: Date={line.date}, Project={line.project_id.name if line.project_id else 'NO PROJECT'}, Hours={line.unit_amount}")
            
    except Exception as e:
        print(f"Error creating/testing approval: {e}")
        import traceback
        traceback.print_exc()

print("\nDiagnostic complete!")
