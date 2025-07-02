#!/usr/bin/env python3
"""
Quick diagnosis script for timesheet approval button visibility issues
Run this in Odoo shell to diagnose approval button problems
"""

def quick_diagnosis(env):
    """Quick diagnosis of approval button issues"""
    
    print("🔍 TIMESHEET APPROVAL BUTTON DIAGNOSIS")
    print("="*50)
    
    user = env.user
    print(f"👤 Current User: {user.name} ({user.login})")
    
    # Check user groups
    print("\n📋 User Groups:")
    groups_to_check = [
        ('System Admin', 'base.group_system'),
        ('HR Manager', 'hr.group_hr_manager'),
        ('Project Manager', 'project.group_project_manager'),
        ('Timesheet User', 'timesheet_approval.group_timesheet_approval_user'),
        ('Timesheet Manager', 'timesheet_approval.group_timesheet_approval_manager'),
    ]
    
    for group_name, group_xml_id in groups_to_check:
        has_group = user.has_group(group_xml_id)
        status = "✅" if has_group else "❌"
        print(f"  {status} {group_name}")
    
    # Check employee record
    employee = user.employee_id
    print(f"\n👨‍💼 Employee Record: {employee.name if employee else '❌ None'}")
    
    if not employee:
        print("🚨 PROBLEM: User has no employee record!")
        print("💡 SOLUTION: Go to Employees menu and create/link employee record")
        return
    
    print(f"   Manager: {employee.parent_id.name if employee.parent_id else '❌ None'}")
    
    if not employee.parent_id:
        print("⚠️  WARNING: Employee has no manager assigned")
        print("💡 SOLUTION: Set manager in employee form")
    
    # Check submitted timesheets
    submitted_timesheets = env['timesheet.approval'].search([
        ('state', '=', 'submitted')
    ])
    
    print(f"\n📊 Submitted Timesheets: {len(submitted_timesheets)}")
    
    if submitted_timesheets:
        approvable_count = 0
        for ts in submitted_timesheets:
            can_approve = ts._can_approve()
            if can_approve:
                approvable_count += 1
            
            print(f"  • {ts.display_name}")
            print(f"    Employee: {ts.employee_id.name}")
            print(f"    Manager: {ts.manager_id.name if ts.manager_id else 'None'}")
            print(f"    Can Approve: {'✅' if can_approve else '❌'}")
        
        print(f"\n✅ You can approve: {approvable_count}/{len(submitted_timesheets)} timesheets")
        
        if approvable_count == 0:
            print("\n🚨 PROBLEM: You cannot approve any submitted timesheets!")
            print("💡 POSSIBLE SOLUTIONS:")
            print("   1. Check if you're assigned as manager for employees")
            print("   2. Verify you have 'Timesheet Approval Manager' group")
            print("   3. Check if manager field is computed correctly on timesheets")
    else:
        print("ℹ️  No submitted timesheets found")
    
    # Quick fix suggestions
    print("\n🔧 QUICK FIXES TO TRY:")
    print("1. Ensure user has employee record")
    print("2. Set employee manager relationships")
    print("3. Add 'Timesheet Approval Manager' group to user")
    print("4. Check timesheet approval records have manager_id set")
    
    print("\n" + "="*50)

def fix_common_issues(env):
    """Fix common setup issues"""
    
    print("🔧 FIXING COMMON ISSUES")
    print("="*30)
    
    user = env.user
    
    # Fix 1: Ensure user has timesheet approval user group
    user_group = env.ref('timesheet_approval.group_timesheet_approval_user')
    if user_group not in user.groups_id:
        user.groups_id = [(4, user_group.id)]
        print("✅ Added Timesheet Approval User group")
    
    # Fix 2: If user manages employees, add manager group
    if user.employee_id:
        direct_reports = env['hr.employee'].search([
            ('parent_id', '=', user.employee_id.id)
        ])
        
        if direct_reports:
            manager_group = env.ref('timesheet_approval.group_timesheet_approval_manager')
            if manager_group not in user.groups_id:
                user.groups_id = [(4, manager_group.id)]
                print(f"✅ Added Timesheet Approval Manager group (manages {len(direct_reports)} employees)")
    
    # Fix 3: Recompute manager_id on all timesheet approvals
    all_approvals = env['timesheet.approval'].search([])
    if all_approvals:
        all_approvals._compute_manager_id()
        print(f"✅ Recomputed manager_id for {len(all_approvals)} timesheet approvals")
    
    # Fix 4: Ensure can_approve_ui is computed
    submitted_approvals = env['timesheet.approval'].search([('state', '=', 'submitted')])
    if submitted_approvals:
        submitted_approvals._compute_can_approve_ui()
        print(f"✅ Recomputed can_approve_ui for {len(submitted_approvals)} submitted approvals")
    
    print("🎉 Common fixes applied!")

if __name__ == '__main__':
    # Run in Odoo shell:
    # ./odoo-bin shell -d your_database
    # exec(open('quick_timesheet_diagnosis.py').read())
    # quick_diagnosis(env)
    # fix_common_issues(env)
    pass
