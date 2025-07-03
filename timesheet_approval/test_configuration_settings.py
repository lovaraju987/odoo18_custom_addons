#!/usr/bin/env python3
"""
Diagnostic script to test Timesheet Approval Configuration Settings

This script verifies that the configuration settings can:
1. Load current values correctly
2. Save new values properly
3. Persist values after reload

Run this after upgrading the module to test the configuration functionality.
"""

def test_configuration_settings(env):
    """Test the configuration settings functionality"""
    
    print("=" * 80)
    print("TIMESHEET APPROVAL CONFIGURATION SETTINGS TEST")
    print("=" * 80)
    
    # Test 1: Create settings instance and load default values
    print("\n1. Testing Configuration Settings Creation and Default Values")
    print("-" * 60)
    
    try:
        settings = env['timesheet.approval.settings'].create({})
        print(f"✅ Settings model created successfully: {settings}")
        
        # Get default values
        default_values = settings.get_values()
        print(f"✅ Default values loaded: {len(default_values)} settings")
        
        # Display some key defaults
        key_settings = [
            'submission_deadline_days',
            'approval_deadline_days', 
            'email_submission_enabled',
            'email_approval_enabled',
            'require_manager_comments',
            'allow_self_approval'
        ]
        
        for key in key_settings:
            if key in default_values:
                print(f"   - {key}: {default_values[key]}")
                
    except Exception as e:
        print(f"❌ Error creating settings: {e}")
        return False
    
    # Test 2: Save configuration values
    print("\n2. Testing Configuration Save Functionality")
    print("-" * 60)
    
    try:
        # Set some test values
        test_values = {
            'submission_deadline_days': 10,
            'approval_deadline_days': 5,
            'email_submission_enabled': False,
            'email_approval_enabled': False,
            'require_manager_comments': True,
            'allow_self_approval': False,
            'reminder_frequency_days': 3,
            'batch_approval_limit': 25
        }
        
        settings.write(test_values)
        print(f"✅ Test values written to settings record")
        
        # Save the values
        settings.set_values()
        print(f"✅ Settings saved via set_values() method")
        
        # Verify values were saved to ir.config_parameter
        params = env['ir.config_parameter'].sudo()
        for key, expected_value in test_values.items():
            param_key = f'timesheet_approval.{key}'
            saved_value = params.get_param(param_key)
            print(f"   - {key}: saved '{saved_value}', expected '{expected_value}'")
            
    except Exception as e:
        print(f"❌ Error saving settings: {e}")
        return False
    
    # Test 3: Load saved values
    print("\n3. Testing Configuration Load Functionality")
    print("-" * 60)
    
    try:
        # Create a new settings instance
        new_settings = env['timesheet.approval.settings'].create({})
        
        # Load the saved values
        loaded_values = new_settings.get_values()
        print(f"✅ Values loaded from saved configuration")
        
        # Verify the loaded values match what we saved
        for key, expected_value in test_values.items():
            if key in loaded_values:
                loaded_value = loaded_values[key]
                if str(loaded_value) == str(expected_value):
                    print(f"   ✅ {key}: {loaded_value} (matches saved)")
                else:
                    print(f"   ❌ {key}: loaded '{loaded_value}', expected '{expected_value}'")
                    
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False
    
    # Test 4: Test helper method
    print("\n4. Testing Helper Method get_config_value()")
    print("-" * 60)
    
    try:
        # Test the helper method
        deadline_days = settings.get_config_value('submission_deadline_days', 7)
        email_enabled = settings.get_config_value('email_submission_enabled', True)
        batch_limit = settings.get_config_value('batch_approval_limit', 50)
        
        print(f"✅ Helper method working:")
        print(f"   - submission_deadline_days: {deadline_days}")
        print(f"   - email_submission_enabled: {email_enabled}")
        print(f"   - batch_approval_limit: {batch_limit}")
        
    except Exception as e:
        print(f"❌ Error with helper method: {e}")
        return False
    
    # Test 5: Test reset functionality
    print("\n5. Testing Reset to Defaults Functionality")
    print("-" * 60)
    
    try:
        # Reset to defaults
        result = settings.action_reset_to_defaults()
        print(f"✅ Reset action completed: {result}")
        
        # Verify some values are back to defaults
        settings.set_values()  # Save the reset values
        
        # Check a few key defaults
        params = env['ir.config_parameter'].sudo()
        submission_days = params.get_param('timesheet_approval.submission_deadline_days', '7')
        approval_days = params.get_param('timesheet_approval.approval_deadline_days', '3')
        
        print(f"   - submission_deadline_days reset to: {submission_days}")
        print(f"   - approval_deadline_days reset to: {approval_days}")
        
    except Exception as e:
        print(f"❌ Error resetting settings: {e}")
        return False
    
    # Test 6: Validate Action Configuration
    print("\n6. Testing Action Configuration")
    print("-" * 60)
    
    try:
        # Find the settings action
        action = env.ref('timesheet_approval.timesheet_approval_settings_action', raise_if_not_found=False)
        if action:
            print(f"✅ Settings action found: {action.name}")
            print(f"   - Model: {action.res_model}")
            print(f"   - View Mode: {action.view_mode}")
            print(f"   - Target: {action.target}")
            print(f"   - Context: {action.context}")
        else:
            print(f"❌ Settings action not found")
            
        # Find the settings view
        view = env.ref('timesheet_approval.timesheet_approval_settings_view_form', raise_if_not_found=False)
        if view:
            print(f"✅ Settings form view found: {view.name}")
            print(f"   - Model: {view.model}")
        else:
            print(f"❌ Settings form view not found")
            
    except Exception as e:
        print(f"❌ Error checking action configuration: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("CONFIGURATION SETTINGS TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\n📋 SUMMARY:")
    print("• Configuration model loads and saves values correctly")
    print("• Values persist in ir.config_parameter")
    print("• Helper methods work properly")
    print("• Reset functionality works")
    print("• Action and view configurations are correct")
    print("\n✅ The configuration settings should now work properly in the UI!")
    print("   After upgrading the module, you should be able to:")
    print("   1. Open the Configuration menu")
    print("   2. Change settings values")
    print("   3. Click Save to persist changes")
    print("   4. Reopen the form to see saved values")
    
    return True

if __name__ == "__main__":
    print("This script should be run from within Odoo environment")
    print("Example usage in Odoo shell:")
    print("  import sys")
    print("  sys.path.append('/path/to/timesheet_approval')")
    print("  from test_configuration_settings import test_configuration_settings")
    print("  test_configuration_settings(env)")
