#!/usr/bin/env python3
"""
EMERGENCY FIX for timesheet approval buttons
This will force the buttons to show by checking and fixing common issues
"""

def emergency_button_fix(env):
    """Emergency fix for missing approval buttons"""
    
    print("🚨 EMERGENCY BUTTON FIX")
    print("="*40)
    
    current_user = env.user
    print(f"Current User: {current_user.name}")
    
    # Step 1: Force add all necessary groups to current user
    groups_to_add = [
        'timesheet_approval.group_timesheet_approval_user',
        'timesheet_approval.group_timesheet_approval_manager',
        'hr.group_hr_manager'  # Often needed for approval permissions
    ]
    
    for group_xml_id in groups_to_add:
        try:
            group = env.ref(group_xml_id)
            if group not in current_user.groups_id:
                current_user.groups_id = [(4, group.id)]
                print(f"✅ Added group: {group.name}")
            else:
                print(f"✓ Already has group: {group.name}")
        except Exception as e:
            print(f"❌ Error with group {group_xml_id}: {e}")
    
    # Step 2: Check current user's employee record
    if not current_user.employee_id:
        print("❌ Current user has no employee record!")
        print("Creating employee record...")
        employee = env['hr.employee'].create({
            'name': current_user.name,
            'user_id': current_user.id,
            'work_email': current_user.email,
        })
        print(f"✅ Created employee record: {employee.name}")
    else:
        print(f"✓ Employee record exists: {current_user.employee_id.name}")
    
    # Step 3: Force recompute manager assignments
    all_approvals = env['timesheet.approval'].search([])
    for approval in all_approvals:
        if approval.employee_id and approval.employee_id.parent_id and not approval.manager_id:
            approval.manager_id = approval.employee_id.parent_id
            print(f"✅ Fixed manager for {approval.display_name}")
    
    # Step 4: Check specific submitted timesheets
    submitted = env['timesheet.approval'].search([('state', '=', 'submitted')])
    print(f"\n📋 Checking {len(submitted)} submitted timesheets:")
    
    for approval in submitted:
        print(f"\n  {approval.display_name}")
        print(f"    Employee: {approval.employee_id.name}")
        print(f"    Manager: {approval.manager_id.name if approval.manager_id else 'NONE'}")
        
        # Force assign current user as manager if none exists
        if not approval.manager_id and current_user.employee_id:
            approval.manager_id = current_user.employee_id
            print(f"    ✅ Assigned current user as manager")
        
        can_approve = approval._can_approve()
        print(f"    Can approve: {'✅' if can_approve else '❌'}")
    
    # Step 5: Clear cache and force refresh
    env.clear()
    
    print(f"\n🎉 EMERGENCY FIX COMPLETE!")
    print(f"Please refresh your browser and check the timesheet approval form again.")
    print(f"The approve/reject buttons should now be visible.")

def verify_fix(env):
    """Verify that the fix worked"""
    
    print("\n🔍 VERIFYING FIX")
    print("="*20)
    
    current_user = env.user
    submitted = env['timesheet.approval'].search([('state', '=', 'submitted')])
    
    print(f"User: {current_user.name}")
    print(f"Has Manager Group: {current_user.has_group('timesheet_approval.group_timesheet_approval_manager')}")
    print(f"Submitted Timesheets: {len(submitted)}")
    
    can_approve_any = False
    for approval in submitted:
        can_approve = approval._can_approve()
        if can_approve:
            can_approve_any = True
            print(f"✅ Can approve: {approval.display_name}")
        else:
            print(f"❌ Cannot approve: {approval.display_name}")
    
    if can_approve_any:
        print("\n🎉 SUCCESS! You should be able to see approve/reject buttons")
    else:
        print("\n❌ ISSUE PERSISTS: You still cannot approve any timesheets")
        print("    Please check manager assignments and user groups manually")

if __name__ == '__main__':
    # Run in Odoo shell:
    # ./odoo-bin shell -d your_database
    # exec(open('emergency_button_fix.py').read())
    # emergency_button_fix(env)
    # verify_fix(env)
    pass
