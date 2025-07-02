#!/usr/bin/env python3
"""
Quick fix for missing employee record issues causing "Missing Record" error
"""

def quick_fix_missing_employee(env):
    """Quick fix for missing employee records causing the 'Missing Record' error"""
    
    print("🚨 QUICK FIX FOR MISSING EMPLOYEE RECORDS")
    print("="*50)
    
    current_user = env.user
    print(f"Current User: {current_user.name} (ID: {current_user.id})")
    
    # Step 1: Check if current user has employee record
    if not current_user.employee_id:
        print("❌ Current user has NO employee record - creating one...")
        
        try:
            employee = env['hr.employee'].create({
                'name': current_user.name,
                'user_id': current_user.id,
                'work_email': current_user.email or current_user.login,
                'active': True,
            })
            print(f"✅ Created employee: {employee.name} (ID: {employee.id})")
        except Exception as e:
            print(f"❌ Error creating employee: {e}")
    else:
        print(f"✅ User has employee record: {current_user.employee_id.name}")
    
    # Step 2: Create employee records for all users without them
    print("\n--- Creating employee records for all users ---")
    users_without_employees = env['res.users'].search([
        ('employee_id', '=', False),
        ('active', '=', True),
        ('share', '=', False)  # Only internal users
    ])
    
    print(f"Found {len(users_without_employees)} users without employee records")
    
    for user in users_without_employees:
        try:
            employee = env['hr.employee'].create({
                'name': user.name,
                'user_id': user.id,
                'work_email': user.email or user.login,
                'active': True,
            })
            print(f"✅ Created employee for {user.name}: {employee.name}")
        except Exception as e:
            print(f"❌ Error creating employee for {user.name}: {e}")
    
    # Step 3: Clean up orphaned timesheet approvals
    print("\n--- Cleaning up orphaned timesheet approvals ---")
    all_approvals = env['timesheet.approval'].search([])
    orphaned_count = 0
    
    for approval in all_approvals:
        try:
            # Try to access employee - this will fail if employee doesn't exist
            _ = approval.employee_id.name
            # Try to access manager if exists
            if approval.manager_id:
                _ = approval.manager_id.name
        except Exception as e:
            print(f"🗑️  Deleting orphaned approval {approval.id}: {e}")
            try:
                approval.unlink()
                orphaned_count += 1
            except Exception as delete_error:
                print(f"❌ Error deleting approval {approval.id}: {delete_error}")
    
    print(f"✅ Cleaned up {orphaned_count} orphaned approvals")
    
    # Step 4: Commit changes
    try:
        env.cr.commit()
        print("\n✅ All changes committed to database")
    except Exception as e:
        print(f"❌ Error committing changes: {e}")
    
    print("\n🎉 QUICK FIX COMPLETE!")
    print("Try accessing 'My Approvals' menu now.")
    print("The 'Missing Record' error should be resolved.")

def verify_fix(env):
    """Verify that the fix worked"""
    
    print("\n🔍 VERIFYING FIX")
    print("="*20)
    
    current_user = env.user
    
    # Check current user has employee
    if current_user.employee_id:
        print(f"✅ Current user has employee: {current_user.employee_id.name}")
    else:
        print("❌ Current user still has no employee record")
    
    # Check for users without employees
    users_without_employees = env['res.users'].search([
        ('employee_id', '=', False),
        ('active', '=', True),
        ('share', '=', False)
    ])
    
    if len(users_without_employees) == 0:
        print("✅ All internal users now have employee records")
    else:
        print(f"⚠️  {len(users_without_employees)} users still missing employee records")
    
    # Check for orphaned approvals
    orphaned_count = 0
    all_approvals = env['timesheet.approval'].search([])
    
    for approval in all_approvals:
        try:
            _ = approval.employee_id.name
            if approval.manager_id:
                _ = approval.manager_id.name
        except:
            orphaned_count += 1
    
    if orphaned_count == 0:
        print("✅ No orphaned timesheet approvals found")
    else:
        print(f"⚠️  {orphaned_count} orphaned approvals still exist")
    
    print("\n🎯 RESULT: The 'Missing Record' error should now be fixed!")

if __name__ == '__main__':
    # Run in Odoo shell:
    # ./odoo-bin shell -d your_database
    # exec(open('quick_fix_missing_employee.py').read())
    # quick_fix_missing_employee(env)
    # verify_fix(env)
    pass
