#!/usr/bin/env python3
"""
Debug script to analyze approve/reject button visibility issues
"""

import logging
_logger = logging.getLogger(__name__)

def debug_approval_permissions(env):
    """Debug approval permissions and button visibility"""
    
    print("\n" + "="*80)
    print("TIMESHEET APPROVAL BUTTON DEBUG ANALYSIS")
    print("="*80)
    
    # Get current user
    current_user = env.user
    print(f"\nCurrent User: {current_user.name} (ID: {current_user.id})")
    print(f"Login: {current_user.login}")
    
    # Check user groups
    print("\n--- USER GROUPS ---")
    relevant_groups = [
        'base.group_system',
        'hr.group_hr_manager', 
        'project.group_project_manager',
        'timesheet_approval.group_timesheet_approval_user',
        'timesheet_approval.group_timesheet_approval_manager'
    ]
    
    for group_xml_id in relevant_groups:
        try:
            group = env.ref(group_xml_id)
            has_group = current_user.has_group(group_xml_id)
            print(f"  {group.name}: {'✓ YES' if has_group else '✗ NO'}")
        except Exception as e:
            print(f"  {group_xml_id}: ERROR - {e}")
    
    # Check employee record
    print("\n--- EMPLOYEE INFORMATION ---")
    employee = current_user.employee_id
    if employee:
        print(f"Employee: {employee.name} (ID: {employee.id})")
        print(f"Manager: {employee.parent_id.name if employee.parent_id else 'No manager set'}")
        print(f"Timesheet Manager: {employee.timesheet_manager_id.name if employee.timesheet_manager_id else 'No timesheet manager'}")
        print(f"Timesheet Approval Required: {employee.timesheet_approval_required}")
    else:
        print("No employee record found for current user!")
        return
    
    # Find timesheet approvals
    print("\n--- TIMESHEET APPROVALS ---")
    approvals = env['timesheet.approval'].search([])
    print(f"Total timesheet approvals: {len(approvals)}")
    
    submitted_approvals = approvals.filtered(lambda a: a.state == 'submitted')
    print(f"Submitted approvals: {len(submitted_approvals)}")
    
    if submitted_approvals:
        print("\nSubmitted approvals details:")
        for approval in submitted_approvals[:5]:  # Show first 5
            print(f"  - {approval.display_name}")
            print(f"    Employee: {approval.employee_id.name}")
            print(f"    Manager: {approval.manager_id.name if approval.manager_id else 'No manager'}")
            print(f"    Date Range: {approval.date_from} to {approval.date_to}")
            print(f"    State: {approval.state}")
            
            # Check if current user can approve
            can_approve = approval._can_approve()
            print(f"    Can current user approve: {'✓ YES' if can_approve else '✗ NO'}")
            
            # Detailed approval check
            print(f"    Detailed approval check:")
            print(f"      - Is system admin: {current_user.has_group('base.group_system')}")
            print(f"      - Is HR manager: {current_user.has_group('hr.group_hr_manager')}")
            print(f"      - Is assigned manager: {approval.manager_id and approval.manager_id.user_id == current_user}")
            print(f"      - Manager user: {approval.manager_id.user_id.name if approval.manager_id and approval.manager_id.user_id else 'None'}")
            
            # Check project manager permission
            if current_user.has_group('project.group_project_manager'):
                project_ids = approval.timesheet_line_ids.mapped('project_id')
                managed_projects = env['project.project'].search([
                    ('user_id', '=', current_user.id),
                    ('id', 'in', project_ids.ids)
                ])
                print(f"      - Project manager for relevant projects: {len(managed_projects) > 0}")
                if project_ids:
                    print(f"        Projects in timesheet: {', '.join(project_ids.mapped('name'))}")
                if managed_projects:
                    print(f"        Managed projects: {', '.join(managed_projects.mapped('name'))}")
    
    # Check access rights
    print("\n--- ACCESS RIGHTS ---")
    try:
        approval_model = env['timesheet.approval']
        print(f"Can read timesheet.approval: {approval_model.check_access_rights('read', raise_exception=False)}")
        print(f"Can write timesheet.approval: {approval_model.check_access_rights('write', raise_exception=False)}")
        print(f"Can create timesheet.approval: {approval_model.check_access_rights('create', raise_exception=False)}")
        print(f"Can unlink timesheet.approval: {approval_model.check_access_rights('unlink', raise_exception=False)}")
    except Exception as e:
        print(f"Error checking access rights: {e}")
    
    # Check record rules
    print("\n--- RECORD RULES ---")
    try:
        # Find which records the user can access
        accessible_approvals = env['timesheet.approval'].search([])
        print(f"Accessible timesheet approvals: {len(accessible_approvals)}")
        
        submitted_accessible = accessible_approvals.filtered(lambda a: a.state == 'submitted')
        print(f"Accessible submitted approvals: {len(submitted_accessible)}")
        
        if submitted_accessible:
            print("First few accessible submitted approvals:")
            for approval in submitted_accessible[:3]:
                print(f"  - {approval.display_name} (Employee: {approval.employee_id.name})")
        
    except Exception as e:
        print(f"Error checking record access: {e}")
    
    # Check team/managed employees
    print("\n--- TEAM MANAGEMENT ---")
    if employee:
        # Find employees where current employee is manager
        managed_employees = env['hr.employee'].search([('parent_id', '=', employee.id)])
        print(f"Direct reports: {len(managed_employees)}")
        if managed_employees:
            print(f"  Managed employees: {', '.join(managed_employees.mapped('name'))}")
        
        # Find approvals for managed employees
        managed_approvals = env['timesheet.approval'].search([
            ('employee_id', 'in', managed_employees.ids),
            ('state', '=', 'submitted')
        ])
        print(f"Pending approvals for managed employees: {len(managed_approvals)}")
    
    print("\n" + "="*80)
    print("DEBUG ANALYSIS COMPLETE")
    print("="*80)

if __name__ == '__main__':
    # This would be run in Odoo shell
    # ./odoo-bin shell -d database_name
    # exec(open('/path/to/debug_approval_buttons.py').read())
    pass
