# Simple Odoo Shell Commands for Debugging Timesheet Submission Issue
# 
# Run these commands in Odoo shell to diagnose the issue:
# 
# 1. Start Odoo shell:
#    python odoo-bin shell -d your_database_name
# 
# 2. Copy and paste these commands one by one:

# Find the employee
employee = env['hr.employee'].search([('name', '=', 'Lovaraju Mylapalli')], limit=1)
print(f"Employee found: {employee.name if employee else 'NOT FOUND'}")

# Check timesheet entries
if employee:
    entries = env['account.analytic.line'].search([
        ('employee_id', '=', employee.id),
        ('date', '>=', '2025-06-30'),
        ('date', '<=', '2025-07-06'),
    ])
    print(f"Total entries found: {len(entries)}")
    
    for entry in entries:
        print(f"  - Date: {entry.date}, Project: {entry.project_id.name if entry.project_id else 'NO PROJECT'}, Hours: {entry.unit_amount}")

# Check if manager is assigned
if employee:
    print(f"Manager: {employee.parent_id.name if employee.parent_id else 'NO MANAGER ASSIGNED'}")

# Test creating an approval record manually
if employee and employee.parent_id:
    approval = env['timesheet.approval'].create({
        'employee_id': employee.id,
        'date_from': '2025-06-30',
        'date_to': '2025-07-06',
    })
    print(f"Created approval: {approval.id}")
    
    # Try to load timesheet lines
    try:
        approval._load_timesheet_lines()
        print(f"Timesheet lines loaded: {len(approval.timesheet_line_ids)}")
        
        # Try to submit
        approval.action_submit()
        print("SUCCESS: Approval submitted!")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

print("Diagnostic complete!")
