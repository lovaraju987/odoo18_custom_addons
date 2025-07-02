"""
Comprehensive diagnostic script for timesheet wizard issue
Run this in Odoo shell to check all aspects of the timesheet system

Usage:
./odoo-bin shell -d your_database_name
>>> exec(open('/path/to/this/script.py').read())
"""

def debug_timesheet_wizard():
    """Debug the timesheet wizard and submission process"""
    
    print("=== TIMESHEET WIZARD DIAGNOSTIC ===\n")
    
    # 1. Check current user and employee
    user = env.user
    print(f"Current User: {user.name} (ID: {user.id})")
    
    employee = env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
    if not employee:
        print("❌ No employee record found for current user!")
        employees = env['hr.employee'].search([], limit=5)
        if employees:
            employee = employees[0]
            print(f"🔄 Using first available employee: {employee.name}")
        else:
            print("❌ No employees found in system at all!")
            return
    else:
        print(f"✅ Employee: {employee.name} (ID: {employee.id})")
    
    # 2. Check manager assignment
    if employee.parent_id:
        print(f"✅ Manager: {employee.parent_id.name}")
    else:
        print("⚠️  No manager assigned to employee")
    
    # 3. Check timesheet entries
    from datetime import datetime, timedelta
    today = datetime.now().date()
    start_date = today - timedelta(days=30)  # Last 30 days
    end_date = today
    
    print(f"\n=== CHECKING TIMESHEET ENTRIES ===")
    print(f"Date range: {start_date} to {end_date}")
    
    # Check account.analytic.line (base timesheet entries)
    timesheet_lines = env['account.analytic.line'].search([
        ('employee_id', '=', employee.id),
        ('date', '>=', start_date),
        ('date', '<=', end_date),
    ])
    
    print(f"Found {len(timesheet_lines)} timesheet entries in account.analytic.line")
    
    if timesheet_lines:
        print("Sample entries:")
        for i, line in enumerate(timesheet_lines[:5]):  # Show first 5
            project_name = line.project_id.name if line.project_id else "NO PROJECT"
            task_name = line.task_id.name if line.task_id else "NO TASK"
            print(f"  {i+1}. Date: {line.date}, Project: {project_name}, Task: {task_name}")
            print(f"      Hours: {line.unit_amount}, Description: {line.name or 'No description'}")
    else:
        print("❌ No timesheet entries found!")
        
        # Check if there are ANY timesheet entries for this employee
        all_entries = env['account.analytic.line'].search([('employee_id', '=', employee.id)])
        print(f"Total timesheet entries for this employee: {len(all_entries)}")
        
        if all_entries:
            latest = all_entries[-1]
            print(f"Latest entry: {latest.date} - {latest.name}")
    
    # 4. Test wizard creation
    print(f"\n=== TESTING WIZARD CREATION ===")
    
    try:
        # Create wizard context similar to how Odoo does it
        wizard_vals = {
            'employee_id': employee.id,
            'date_from': start_date,
            'date_to': end_date,
        }
        
        # Create the wizard
        wizard = env['timesheet.submission.wizard'].create(wizard_vals)
        print(f"✅ Created wizard: ID {wizard.id}")
        print(f"   Employee: {wizard.employee_id.name}")
        print(f"   Date range: {wizard.date_from} to {wizard.date_to}")
        print(f"   Include entries without projects: {wizard.include_entries_without_projects}")
        
        # Test the preview method
        print(f"\n=== TESTING WIZARD PREVIEW ===")
        
        # Call the method that loads timesheet lines
        wizard._load_timesheet_lines()
        
        print(f"Loaded timesheet lines: {len(wizard.timesheet_line_ids)}")
        
        if wizard.timesheet_line_ids:
            print("Preview entries found:")
            for i, line in enumerate(wizard.timesheet_line_ids[:5]):
                project_name = line.project_id.name if line.project_id else "NO PROJECT"
                print(f"  {i+1}. Date: {line.date}, Project: {project_name}, Hours: {line.unit_amount}")
        else:
            print("❌ No entries loaded in wizard preview!")
            
            # Debug the search criteria
            print("\nDebugging search criteria...")
            search_domain = [
                ('employee_id', '=', wizard.employee_id.id),
                ('date', '>=', wizard.date_from),
                ('date', '<=', wizard.date_to),
            ]
            
            if not wizard.include_entries_without_projects:
                search_domain.append(('project_id', '!=', False))
            
            print(f"Search domain: {search_domain}")
            
            # Test the search manually
            manual_search = env['account.analytic.line'].search(search_domain)
            print(f"Manual search result: {len(manual_search)} entries")
            
    except Exception as e:
        print(f"❌ Error creating/testing wizard: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Check existing approvals
    print(f"\n=== CHECKING EXISTING APPROVALS ===")
    
    existing_approvals = env['timesheet.approval'].search([
        ('employee_id', '=', employee.id)
    ])
    
    print(f"Found {len(existing_approvals)} existing timesheet approvals")
    
    for approval in existing_approvals[-3:]:  # Show last 3
        print(f"  - ID: {approval.id}, Period: {approval.date_from} to {approval.date_to}")
        print(f"    State: {approval.state}, Lines: {len(approval.timesheet_line_ids)}")
    
    # 6. Check module configuration
    print(f"\n=== CHECKING MODULE CONFIGURATION ===")
    
    try:
        config = env['timesheet.approval.settings'].search([], limit=1)
        if config:
            print("✅ Configuration found:")
            print(f"   Submission deadline: {config.submission_deadline_days} days")
            print(f"   Email notifications enabled: {config.enable_email_notifications}")
        else:
            print("⚠️  No configuration found - using defaults")
    except Exception as e:
        print(f"⚠️  Configuration check failed: {e}")
    
    # 7. Check database structure
    print(f"\n=== CHECKING DATABASE STRUCTURE ===")
    
    try:
        # Check if timesheet.submission.wizard model exists and is accessible
        wizard_model = env['ir.model'].search([('model', '=', 'timesheet.submission.wizard')])
        if wizard_model:
            print("✅ Wizard model found in database")
        else:
            print("❌ Wizard model NOT found in database!")
        
        # Check if account.analytic.line model is accessible
        analytic_model = env['ir.model'].search([('model', '=', 'account.analytic.line')])
        if analytic_model:
            print("✅ Analytic line model found")
        else:
            print("❌ Analytic line model NOT found!")
            
    except Exception as e:
        print(f"❌ Database structure check failed: {e}")
    
    print(f"\n=== DIAGNOSTIC COMPLETE ===")
    print("If the wizard preview is empty but timesheet entries exist,")
    print("the issue is likely in the wizard's _load_timesheet_lines method")
    print("or in the search domain filtering.")

# Run the diagnostic
debug_timesheet_wizard()
