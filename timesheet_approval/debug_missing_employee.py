#!/usr/bin/env python3
"""
Debug script to diagnose and fix missing employee record issues
"""

import logging
_logger = logging.getLogger(__name__)

def debug_missing_employee(env):
    """Debug missing employee record issues"""
    
    print("\n" + "="*80)
    print("MISSING EMPLOYEE RECORD DIAGNOSIS")
    print("="*80)
    
    # Get current user
    current_user = env.user
    print(f"\nCurrent User: {current_user.name} (ID: {current_user.id})")
    print(f"Login: {current_user.login}")
    
    # Check if current user has employee record
    print("\n--- EMPLOYEE RECORD CHECK ---")
    employee = current_user.employee_id
    if employee:
        print(f"✓ Employee record exists: {employee.name} (ID: {employee.id})")
        print(f"  Active: {employee.active}")
        print(f"  Manager: {employee.parent_id.name if employee.parent_id else 'None'}")
        print(f"  User: {employee.user_id.name if employee.user_id else 'None'}")
    else:
        print("✗ NO EMPLOYEE RECORD for current user!")
        print("This is likely the source of the 'Missing Record' error")
    
    # Check all users without employee records
    print("\n--- USERS WITHOUT EMPLOYEE RECORDS ---")
    users_without_employees = env['res.users'].search([
        ('employee_id', '=', False),
        ('active', '=', True)
    ])
    print(f"Active users without employee records: {len(users_without_employees)}")
    for user in users_without_employees:
        print(f"  - {user.name} (ID: {user.id}, Login: {user.login})")
    
    # Check for orphaned employee references
    print("\n--- ORPHANED EMPLOYEE REFERENCES ---")
    try:
        # Check if employee ID 2 exists
        employee_2 = env['hr.employee'].browse(2)
        if employee_2.exists():
            print(f"✓ Employee ID 2 exists: {employee_2.name}")
            print(f"  Active: {employee_2.active}")
            print(f"  User: {employee_2.user_id.name if employee_2.user_id else 'No user linked'}")
        else:
            print("✗ Employee ID 2 does NOT exist (this is the missing record!)")
    except Exception as e:
        print(f"Error checking employee ID 2: {e}")
    
    # Check timesheet approvals with missing employee references
    print("\n--- TIMESHEET APPROVALS WITH MISSING EMPLOYEES ---")
    try:
        all_approvals = env['timesheet.approval'].search([])
        print(f"Total timesheet approvals: {len(all_approvals)}")
        
        problematic_approvals = []
        for approval in all_approvals:
            try:
                # Try to access employee
                employee_name = approval.employee_id.name
                manager_name = approval.manager_id.name if approval.manager_id else 'None'
            except Exception as e:
                problematic_approvals.append((approval, e))
                print(f"✗ Problem with approval {approval.id}: {e}")
        
        if not problematic_approvals:
            print("✓ All timesheet approvals have valid employee references")
        else:
            print(f"Found {len(problematic_approvals)} problematic approvals")
    except Exception as e:
        print(f"Error checking timesheet approvals: {e}")
    
    # Check menu action and domain
    print("\n--- MENU ACTION ANALYSIS ---")
    try:
        # Find the "My Approvals" menu
        my_approvals_menu = env['ir.ui.menu'].search([
            ('name', '=', 'My Approvals')
        ])
        if my_approvals_menu:
            print(f"✓ Found 'My Approvals' menu: {my_approvals_menu.name}")
            action = my_approvals_menu.action
            if action:
                print(f"  Action: {action.name} (Type: {action._name})")
                if hasattr(action, 'domain'):
                    print(f"  Domain: {action.domain}")
                if hasattr(action, 'context'):
                    print(f"  Context: {action.context}")
        else:
            print("✗ 'My Approvals' menu not found")
    except Exception as e:
        print(f"Error checking menu action: {e}")
    
    # Check current user's approval-related data
    print("\n--- USER'S APPROVAL DATA ---")
    if employee:
        try:
            # Approvals as employee
            employee_approvals = env['timesheet.approval'].search([
                ('employee_id', '=', employee.id)
            ])
            print(f"Approvals as employee: {len(employee_approvals)}")
            
            # Approvals as manager
            manager_approvals = env['timesheet.approval'].search([
                ('manager_id', '=', employee.id)
            ])
            print(f"Approvals as manager: {len(manager_approvals)}")
            
            # Check if any approvals reference non-existent employees
            all_user_related = employee_approvals + manager_approvals
            for approval in all_user_related:
                try:
                    _ = approval.employee_id.name
                    _ = approval.manager_id.name if approval.manager_id else None
                except Exception as e:
                    print(f"  ✗ Problem with approval {approval.id}: {e}")
        except Exception as e:
            print(f"Error checking user's approval data: {e}")
    
    print("\n" + "="*80)
    print("DIAGNOSIS COMPLETE")
    print("="*80)

def fix_missing_employee_issues(env):
    """Fix missing employee record issues"""
    
    print("\n" + "="*80)
    print("FIXING MISSING EMPLOYEE ISSUES")
    print("="*80)
    
    current_user = env.user
    
    # Fix 1: Create employee record for current user if missing
    if not current_user.employee_id:
        print(f"\nCreating employee record for user: {current_user.name}")
        
        # Check if there's an existing employee with same name
        existing_employee = env['hr.employee'].search([
            ('name', '=', current_user.name),
            ('user_id', '=', False)
        ], limit=1)
        
        if existing_employee:
            print(f"Found existing employee {existing_employee.name}, linking to user")
            existing_employee.user_id = current_user.id
            current_user.employee_id = existing_employee.id
        else:
            # Create new employee record
            employee_vals = {
                'name': current_user.name,
                'user_id': current_user.id,
                'work_email': current_user.email or current_user.login,
                'active': True,
            }
            
            new_employee = env['hr.employee'].create(employee_vals)
            print(f"Created new employee record: {new_employee.name} (ID: {new_employee.id})")
            current_user.employee_id = new_employee.id
    else:
        print(f"✓ User already has employee record: {current_user.employee_id.name}")
    
    # Fix 2: Clean up timesheet approvals with missing employee references
    print("\n--- CLEANING UP PROBLEMATIC APPROVALS ---")
    try:
        all_approvals = env['timesheet.approval'].search([])
        problematic_approvals = []
        
        for approval in all_approvals:
            try:
                # Test access to employee and manager
                _ = approval.employee_id.name
                if approval.manager_id:
                    _ = approval.manager_id.name
            except Exception as e:
                problematic_approvals.append(approval)
                print(f"Found problematic approval {approval.id}: {e}")
        
        if problematic_approvals:
            print(f"\nFound {len(problematic_approvals)} problematic approvals")
            
            # Option 1: Try to fix by setting valid employees
            for approval in problematic_approvals:
                try:
                    # If employee_id is invalid, try to find a valid one
                    if not approval.employee_id or not approval.employee_id.exists():
                        # Try to find employee by timesheet lines
                        timesheet_lines = approval.timesheet_line_ids
                        if timesheet_lines:
                            valid_employee = timesheet_lines[0].employee_id
                            if valid_employee and valid_employee.exists():
                                print(f"  Fixing approval {approval.id}: setting employee to {valid_employee.name}")
                                approval.employee_id = valid_employee.id
                                continue
                        
                        # If no valid employee found, delete the approval
                        print(f"  Deleting approval {approval.id}: no valid employee reference found")
                        approval.unlink()
                    
                    # If manager_id is invalid, clear it
                    if approval.exists() and approval.manager_id and not approval.manager_id.exists():
                        print(f"  Clearing invalid manager for approval {approval.id}")
                        approval.manager_id = False
                        
                except Exception as e:
                    print(f"  Error fixing approval {approval.id}: {e}")
                    try:
                        # Last resort: delete the problematic approval
                        approval.unlink()
                        print(f"  Deleted problematic approval {approval.id}")
                    except:
                        pass
        else:
            print("✓ No problematic approvals found")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")
    
    # Fix 3: Ensure all active users have employee records
    print("\n--- ENSURING ALL USERS HAVE EMPLOYEE RECORDS ---")
    users_without_employees = env['res.users'].search([
        ('employee_id', '=', False),
        ('active', '=', True),
        ('share', '=', False)  # Only internal users
    ])
    
    for user in users_without_employees:
        try:
            # Check if there's an existing employee with same name
            existing_employee = env['hr.employee'].search([
                ('name', '=', user.name),
                ('user_id', '=', False)
            ], limit=1)
            
            if existing_employee:
                print(f"Linking existing employee {existing_employee.name} to user {user.name}")
                existing_employee.user_id = user.id
                user.employee_id = existing_employee.id
            else:
                # Create new employee record
                employee_vals = {
                    'name': user.name,
                    'user_id': user.id,
                    'work_email': user.email or user.login,
                    'active': True,
                }
                
                new_employee = env['hr.employee'].create(employee_vals)
                print(f"Created employee record for user {user.name}: {new_employee.name}")
                user.employee_id = new_employee.id
                
        except Exception as e:
            print(f"Error creating employee for user {user.name}: {e}")
    
    env.cr.commit()
    print("\n✓ All fixes applied and committed")
    
    print("\n" + "="*80)
    print("FIXES COMPLETE")
    print("="*80)

if __name__ == '__main__':
    # This would be run in Odoo shell
    # ./odoo-bin shell -d database_name
    # exec(open('/path/to/debug_missing_employee.py').read())
    # debug_missing_employee(env)
    # fix_missing_employee_issues(env)
    pass
