#!/usr/bin/env python3
"""
Test script to verify leave request date handling
"""

from datetime import datetime

def test_date_parsing():
    """Test the date parsing logic from our controller"""
    
    print("🧪 Testing Leave Request Date Parsing")
    print("=" * 40)
    
    # Test cases that might come from the form
    test_dates = [
        "2025-08-15",
        "2025-12-25", 
        "2025-09-01",
        "2025-10-31"
    ]
    
    for date_str in test_dates:
        try:
            # This is the same logic we use in the controller
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            print(f"✅ Input: '{date_str}' -> Parsed: {date_obj} (type: {type(date_obj)})")
            
            # Test what would go into the vals dictionary
            vals_example = {
                'request_date_from': date_obj,
                'request_date_to': date_obj,
            }
            
            print(f"   📋 Would create vals: {vals_example}")
            
        except Exception as e:
            print(f"❌ Failed to parse '{date_str}': {e}")
    
    print("\n🔍 Debugging Tips:")
    print("1. Check the Odoo logs for the debug messages we added")
    print("2. Verify that the form is sending the correct date format")
    print("3. Make sure no JavaScript is overriding the date values")
    print("4. Check if the hr.leave model has any onchange methods affecting dates")
    
    print("\n📝 What to look for in Odoo logs:")
    print("   - 'Leave Request Debug: Received date_from=...'")
    print("   - 'Leave Request Debug: Parsed date_from_obj=...'") 
    print("   - 'Leave Request Debug: Created leave ID=...'")

if __name__ == "__main__":
    test_date_parsing()
