#!/usr/bin/env python3
"""
Script to fix manager assignments and verify timesheet approval setup
"""

def fix_manager_assignments(env):
    """Fix and verify manager assignments for timesheet approval"""
    
    print("="*60)
    print("FIXING MANAGER ASSIGNMENTS")
    print("="*60)
    
    # Get all employees
    employees = env['hr.employee'].search([])
    print(f"Total employees: {len(employees)}")
    
    # Find employees without managers
    employees_without_managers = employees.filtered(lambda e: not e.parent_id)
    print(f"Employees without managers: {len(employees_without_managers)}")
    
    if employees_without_managers:
        print("\nEmployees without managers:")
        for emp in employees_without_managers:
            user = emp.user_id
            print(f"  - {emp.name} (User: {user.name if user else 'No user'})")
    
    # Find employees with managers but manager has no user
    employees_manager_no_user = employees.filtered(
        lambda e: e.parent_id and not e.parent_id.user_id
    )
    print(f"Employees with managers but manager has no user: {len(employees_manager_no_user)}")
    
    if employees_manager_no_user:
        print("\nEmployees with managers that have no user account:")
        for emp in employees_manager_no_user:
            print(f"  - {emp.name} -> Manager: {emp.parent_id.name} (no user)")
    
    # Check group assignments
    print("\n" + "="*60)
    print("CHECKING USER GROUP ASSIGNMENTS")
    print("="*60)
    
    manager_group = env.ref('timesheet_approval.group_timesheet_approval_manager')
    user_group = env.ref('timesheet_approval.group_timesheet_approval_user')
    
    # Get all users with employee records
    users_with_employees = env['res.users'].search([
        ('employee_id', '!=', False),
        ('active', '=', True)
    ])
    
    print(f"Active users with employee records: {len(users_with_employees)}")
    
    # Check who has manager permissions
    managers = users_with_employees.filtered(lambda u: manager_group in u.groups_id)
    print(f"Users with manager permissions: {len(managers)}")
    
    # Check who should be managers (have direct reports)
    should_be_managers = []
    for user in users_with_employees:
        if user.employee_id:
            direct_reports = env['hr.employee'].search([
                ('parent_id', '=', user.employee_id.id)
            ])
            if direct_reports and manager_group not in user.groups_id:
                should_be_managers.append((user, direct_reports))
    
    if should_be_managers:
        print(f"\nUsers who should have manager permissions: {len(should_be_managers)}")
        for user, reports in should_be_managers:
            print(f"  - {user.name} manages {len(reports)} employees")
            # Add manager group
            user.groups_id = [(4, manager_group.id)]
            print(f"    -> Added manager permissions")
    
    # Ensure all users have user permissions
    users_without_user_group = users_with_employees.filtered(
        lambda u: user_group not in u.groups_id
    )
    
    if users_without_user_group:
        print(f"\nAdding user permissions to {len(users_without_user_group)} users")
        for user in users_without_user_group:
            user.groups_id = [(4, user_group.id)]
            print(f"  - Added user permissions to {user.name}")
    
    print("\n" + "="*60)
    print("CHECKING TIMESHEET APPROVALS")
    print("="*60)
    
    # Check submitted timesheets
    submitted_approvals = env['timesheet.approval'].search([
        ('state', '=', 'submitted')
    ])
    
    print(f"Submitted timesheet approvals: {len(submitted_approvals)}")
    
    if submitted_approvals:
        print("\nSubmitted approvals and their managers:")
        for approval in submitted_approvals:
            manager = approval.manager_id
            manager_user = manager.user_id if manager else None
            can_approve = approval._can_approve()
            
            print(f"  - {approval.display_name}")
            print(f"    Employee: {approval.employee_id.name}")
            print(f"    Manager: {manager.name if manager else 'None'}")
            print(f"    Manager User: {manager_user.name if manager_user else 'None'}")
            print(f"    Current user can approve: {can_approve}")
            
            if not manager:
                print(f"    ⚠️  WARNING: No manager assigned!")
            elif not manager_user:
                print(f"    ⚠️  WARNING: Manager has no user account!")
    
    print("\n" + "="*60)
    print("MANAGER ASSIGNMENT FIX COMPLETE")
    print("="*60)

def verify_approval_setup(env):
    """Verify the complete approval setup"""
    
    print("\n" + "="*60)
    print("VERIFYING APPROVAL SETUP")
    print("="*60)
    
    current_user = env.user
    current_employee = current_user.employee_id
    
    print(f"Current User: {current_user.name}")
    print(f"Current Employee: {current_employee.name if current_employee else 'None'}")
    
    if not current_employee:
        print("❌ ISSUE: Current user has no employee record!")
        return
    
    # Check if user has manager permissions
    has_manager_perms = current_user.has_group('timesheet_approval.group_timesheet_approval_manager')
    print(f"Has manager permissions: {has_manager_perms}")
    
    if has_manager_perms:
        # Find direct reports
        direct_reports = env['hr.employee'].search([
            ('parent_id', '=', current_employee.id)
        ])
        print(f"Direct reports: {len(direct_reports)}")
        
        if direct_reports:
            print("Direct reports:")
            for emp in direct_reports:
                user = emp.user_id
                print(f"  - {emp.name} (User: {user.name if user else 'No user'})")
        
        # Find timesheets that can be approved
        approvals_can_approve = env['timesheet.approval'].search([
            ('state', '=', 'submitted')
        ]).filtered(lambda a: a._can_approve())
        
        print(f"Timesheets current user can approve: {len(approvals_can_approve)}")
        
        if approvals_can_approve:
            print("Approvable timesheets:")
            for approval in approvals_can_approve:
                print(f"  - {approval.display_name}")
    
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)

if __name__ == '__main__':
    # Run in Odoo shell:
    # ./odoo-bin shell -d database_name
    # exec(open('fix_manager_permissions.py').read())
    # fix_manager_assignments(env)
    # verify_approval_setup(env)
    pass
