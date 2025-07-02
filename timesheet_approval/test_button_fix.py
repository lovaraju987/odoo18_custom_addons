#!/usr/bin/env python3
"""
Test script to verify the button fix
"""

def test_button_visibility(env):
    """Test if the buttons are now visible"""
    
    print("🧪 TESTING BUTTON VISIBILITY")
    print("="*40)
    
    # Check if the new view exists
    form_view = env['ir.ui.view'].search([
        ('name', '=', 'timesheet.approval.form.fixed'),
        ('model', '=', 'timesheet.approval')
    ])
    
    if form_view:
        print("✅ New form view found")
        print(f"View ID: {form_view.id}")
        print(f"View Name: {form_view.name}")
        
        # Check if it contains the buttons
        if 'action_approve' in form_view.arch_db:
            print("✅ Approve button found in view")
        else:
            print("❌ Approve button NOT found in view")
            
        if 'action_reject' in form_view.arch_db:
            print("✅ Reject button found in view")
        else:
            print("❌ Reject button NOT found in view")
    else:
        print("❌ New form view NOT found - module needs updating")
    
    # Check actions
    action = env['ir.actions.act_window'].search([
        ('name', '=', 'Timesheet Approvals'),
        ('res_model', '=', 'timesheet.approval')
    ])
    
    if action:
        print(f"✅ Manager action found: {action.name}")
        if action.view_id:
            print(f"   References view: {action.view_id.name}")
        else:
            print("   No specific view referenced")
    
    # Test with actual timesheet
    submitted = env['timesheet.approval'].search([('state', '=', 'submitted')], limit=1)
    if submitted:
        print(f"\n📋 Testing with: {submitted.display_name}")
        print(f"State: {submitted.state}")
        
        # Since we removed all invisible conditions, buttons should be visible
        print("💡 Buttons should now be visible (no conditions applied)")
    else:
        print("\n⚠️  No submitted timesheets found to test with")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Upgrade the module: ./odoo-bin -d db_name -u timesheet_approval --stop-after-init")
    print("2. Refresh browser and check timesheet form")
    print("3. Buttons should be visible at the top")

if __name__ == '__main__':
    # Run in Odoo shell:
    # ./odoo-bin shell -d your_database
    # exec(open('test_button_fix.py').read())
    # test_button_visibility(env)
    pass
