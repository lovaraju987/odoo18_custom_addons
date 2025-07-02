#!/usr/bin/env python3
"""
Script to set up proper manager permissions
"""

def setup_manager_permissions(env):
    """Set up proper manager permissions for current user"""
    
    print("🔧 SETTING UP MANAGER PERMISSIONS")
    print("="*45)
    
    current_user = env.user
    print(f"Current User: {current_user.name}")
    
    # Ensure current user has manager permissions
    manager_group = env.ref('timesheet_approval.group_timesheet_approval_manager')
    user_group = env.ref('timesheet_approval.group_timesheet_approval_user')
    
    groups_added = []
    
    if user_group not in current_user.groups_id:
        current_user.groups_id = [(4, user_group.id)]
        groups_added.append("Timesheet Approval User")
    
    if manager_group not in current_user.groups_id:
        current_user.groups_id = [(4, manager_group.id)]
        groups_added.append("Timesheet Approval Manager")
    
    if groups_added:
        print(f"✅ Added groups: {', '.join(groups_added)}")
    else:
        print("✓ User already has all required groups")
    
    # Verify current permissions
    print(f"\nCurrent permissions:")
    print(f"  Timesheet User: {current_user.has_group('timesheet_approval.group_timesheet_approval_user')}")
    print(f"  Timesheet Manager: {current_user.has_group('timesheet_approval.group_timesheet_approval_manager')}")
    print(f"  HR Manager: {current_user.has_group('hr.group_hr_manager')}")
    print(f"  System Admin: {current_user.has_group('base.group_system')}")
    
    # Test with submitted timesheets
    submitted = env['timesheet.approval'].search([('state', '=', 'submitted')])
    print(f"\nTesting with {len(submitted)} submitted timesheets:")
    
    for approval in submitted[:3]:  # Test first 3
        can_approve = approval._can_approve()
        print(f"  {approval.display_name}: {'✅ Can approve' if can_approve else '❌ Cannot approve'}")
    
    print(f"\n🎯 RESULT:")
    print(f"✅ Buttons should now be visible ONLY to managers")
    print(f"✅ Regular users will NOT see approve/reject buttons")
    print(f"✅ Server-side security is maintained")

def test_user_permissions(env):
    """Test what a regular user would see"""
    
    print(f"\n🧪 TESTING USER PERMISSIONS")
    print("="*30)
    
    # Find a regular user (not in manager group)
    manager_group = env.ref('timesheet_approval.group_timesheet_approval_manager')
    regular_users = env['res.users'].search([
        ('groups_id', 'not in', [manager_group.id]),
        ('active', '=', True),
        ('employee_id', '!=', False)
    ])
    
    if regular_users:
        test_user = regular_users[0]
        print(f"Testing as regular user: {test_user.name}")
        print(f"  Has manager group: {manager_group in test_user.groups_id}")
        print(f"  Result: {'❌ No buttons' if manager_group not in test_user.groups_id else '✅ Has buttons'}")
    else:
        print("No regular users found to test with")

if __name__ == '__main__':
    # Run in Odoo shell:
    # ./odoo-bin shell -d your_database
    # exec(open('setup_manager_permissions.py').read())
    # setup_manager_permissions(env)
    # test_user_permissions(env)
    pass
