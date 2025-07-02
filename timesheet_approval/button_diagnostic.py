#!/usr/bin/env python3
"""
Focused diagnostic script for the specific button visibility issue
Run this to check why buttons are not showing for the current user
"""

def diagnose_button_issue(env):
    """Diagnose why approve/reject buttons are not showing"""
    
    print("🔍 BUTTON VISIBILITY DIAGNOSTIC")
    print("="*50)
    
    current_user = env.user
    print(f"Current User: {current_user.name}")
    print(f"Employee: {current_user.employee_id.name if current_user.employee_id else 'None'}")
    
    # Get the specific submitted timesheet from screenshot
    submitted_approvals = env['timesheet.approval'].search([
        ('state', '=', 'submitted'),
        ('employee_id.name', 'ilike', 'Lovaraju')
    ])
    
    if not submitted_approvals:
        submitted_approvals = env['timesheet.approval'].search([('state', '=', 'submitted')])
    
    print(f"\nFound {len(submitted_approvals)} submitted timesheets")
    
    for approval in submitted_approvals:
        print(f"\n--- Analyzing: {approval.display_name} ---")
        print(f"Employee: {approval.employee_id.name}")
        print(f"Manager: {approval.manager_id.name if approval.manager_id else 'NO MANAGER'}")
        print(f"State: {approval.state}")
        
        # Check if can_approve_ui field exists and its value
        try:
            can_approve_ui = approval.can_approve_ui
            print(f"can_approve_ui field: {can_approve_ui}")
        except AttributeError:
            print("❌ can_approve_ui field MISSING! Need to update module.")
            return
        
        # Check _can_approve method
        can_approve_method = approval._can_approve()
        print(f"_can_approve() method: {can_approve_method}")
        
        # Check user groups
        print(f"\nUser Group Check:")
        print(f"  System Admin: {current_user.has_group('base.group_system')}")
        print(f"  HR Manager: {current_user.has_group('hr.group_hr_manager')}")
        print(f"  Timesheet Manager: {current_user.has_group('timesheet_approval.group_timesheet_approval_manager')}")
        
        # Check manager relationship
        print(f"\nManager Relationship:")
        if approval.manager_id:
            print(f"  Manager: {approval.manager_id.name}")
            print(f"  Manager User: {approval.manager_id.user_id.name if approval.manager_id.user_id else 'NO USER'}")
            print(f"  Is Current User Manager: {approval.manager_id.user_id == current_user if approval.manager_id.user_id else False}")
        else:
            print(f"  ❌ NO MANAGER ASSIGNED!")
        
        # Check employee parent relationship
        if approval.employee_id.parent_id:
            print(f"  Employee Parent: {approval.employee_id.parent_id.name}")
            print(f"  Parent User: {approval.employee_id.parent_id.user_id.name if approval.employee_id.parent_id.user_id else 'NO USER'}")
            print(f"  Is Current User Parent: {approval.employee_id.parent_id.user_id == current_user if approval.employee_id.parent_id.user_id else False}")
        else:
            print(f"  ❌ NO EMPLOYEE PARENT!")
    
    # Check module version and view updates
    print(f"\n--- MODULE STATUS ---")
    module = env['ir.module.module'].search([('name', '=', 'timesheet_approval')])
    if module:
        print(f"Module State: {module.state}")
        print(f"Module Version: {module.latest_version}")
    
    # Check if views are updated
    form_view = env['ir.ui.view'].search([
        ('name', '=', 'timesheet.approval.form'),
        ('model', '=', 'timesheet.approval')
    ])
    
    if form_view:
        print(f"Form view found: {form_view.name}")
        # Check if view contains can_approve_ui
        if 'can_approve_ui' in form_view.arch_db:
            print("✅ Form view contains can_approve_ui")
        else:
            print("❌ Form view does NOT contain can_approve_ui - need to update!")
    
    print("\n" + "="*50)

def quick_fix_attempt(env):
    """Attempt quick fixes for the button issue"""
    
    print("🔧 ATTEMPTING QUICK FIXES")
    print("="*30)
    
    current_user = env.user
    
    # Fix 1: Add manager group if missing
    manager_group = env.ref('timesheet_approval.group_timesheet_approval_manager', raise_if_not_found=False)
    if manager_group and manager_group not in current_user.groups_id:
        current_user.groups_id = [(4, manager_group.id)]
        print("✅ Added manager group to current user")
    
    # Fix 2: Recompute all manager assignments
    all_approvals = env['timesheet.approval'].search([])
    all_approvals._compute_manager_id()
    print(f"✅ Recomputed manager_id for {len(all_approvals)} approvals")
    
    # Fix 3: Force compute can_approve_ui if field exists
    try:
        submitted_approvals = env['timesheet.approval'].search([('state', '=', 'submitted')])
        submitted_approvals._compute_can_approve_ui()
        print(f"✅ Recomputed can_approve_ui for {len(submitted_approvals)} submitted approvals")
    except AttributeError:
        print("❌ can_approve_ui field not found - module needs updating")
    
    # Fix 4: Clear cache
    env.clear()
    print("✅ Cleared environment cache")
    
    print("🎉 Quick fixes completed!")

if __name__ == '__main__':
    # Run in Odoo shell:
    # ./odoo-bin shell -d your_database
    # exec(open('button_diagnostic.py').read())
    # diagnose_button_issue(env)
    # quick_fix_attempt(env)
    pass
