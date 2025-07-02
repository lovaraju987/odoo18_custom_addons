"""
Fix user permissions for timesheet approval
Run this in Odoo shell to assign proper groups to the user
./odoo-bin shell -d your_database_name
>>> exec(open('fix_user_permissions.py').read())
"""

print("=== FIXING USER PERMISSIONS ===")

# Get current user
current_user = env.user
print(f"Current user: {current_user.name} (ID: {current_user.id})")

# Get the required groups
try:
    user_group = env.ref('timesheet_approval.group_timesheet_approval_user')
    manager_group = env.ref('timesheet_approval.group_timesheet_approval_manager')
    print(f"Found groups - User: {user_group.name}, Manager: {manager_group.name}")
except Exception as e:
    print(f"Error finding groups: {e}")
    print("Groups may not exist. Check module installation.")
    exit()

# Check current user's groups
current_groups = current_user.groups_id
print(f"\nCurrent user groups:")
for group in current_groups:
    print(f"  - {group.name}")

# Check if user has timesheet approval groups
has_user_group = user_group in current_groups
has_manager_group = manager_group in current_groups

print(f"\nHas Timesheet Approval User group: {has_user_group}")
print(f"Has Timesheet Approval Manager group: {has_manager_group}")

# Add user to timesheet approval user group if not already there
if not has_user_group:
    print("\nAdding user to Timesheet Approval User group...")
    current_user.write({
        'groups_id': [(4, user_group.id)]
    })
    print("✓ Added to Timesheet Approval User group")
else:
    print("\n✓ User already has Timesheet Approval User group")

# Optionally add to manager group (uncomment if user should be a manager)
# if not has_manager_group:
#     print("\nAdding user to Timesheet Approval Manager group...")
#     current_user.write({
#         'groups_id': [(4, manager_group.id)]
#     })
#     print("✓ Added to Timesheet Approval Manager group")

# Check employee record
employee = current_user.employee_id
if employee:
    print(f"\nEmployee record: {employee.name}")
    if not employee.parent_id:
        print("WARNING: Employee has no manager assigned!")
        print("Setting self as manager for testing...")
        employee.write({'parent_id': employee.id})
        print("✓ Self-assigned as manager")
    else:
        print(f"Manager: {employee.parent_id.name}")
else:
    print("\nERROR: User has no employee record!")
    print("Creating employee record...")
    employee = env['hr.employee'].create({
        'name': current_user.name,
        'user_id': current_user.id,
        'parent_id': False,  # Will be set below
    })
    # Set self as manager for testing
    employee.write({'parent_id': employee.id})
    print("✓ Created employee record with self as manager")

print("\n=== PERMISSIONS FIXED ===")
print("Try the timesheet submission wizard again!")
