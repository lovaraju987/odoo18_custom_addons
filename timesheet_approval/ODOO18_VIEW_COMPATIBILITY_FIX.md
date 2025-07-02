# Odoo 18 View Compatibility Fix

## Issue Resolved
**Error**: `Since 17.0, the "attrs" and "states" attributes are no longer used.`

## Root Cause
The XML view file contained deprecated `attrs` attribute syntax that was replaced in Odoo 17+:

```xml
<!-- OLD (Deprecated in Odoo 18) -->
<div attrs="{'invisible': [('auto_approve_standard_hours', '=', False)]}">

<!-- NEW (Odoo 18 Compatible) -->
<div invisible="not auto_approve_standard_hours">
```

## Fix Applied
**File Modified**: `views/timesheet_approval_settings_views.xml`
- **Line 188**: Updated `attrs="{'invisible': [('auto_approve_standard_hours', '=', False)]}"` to `invisible="not auto_approve_standard_hours"`
- **Impact**: View now compatible with Odoo 18 syntax requirements

## Odoo 18 View Attribute Changes
In Odoo 18, the following changes were made:
- ❌ `attrs="{'invisible': [('field', '=', value)]}"` (deprecated)
- ✅ `invisible="field != value"` (new syntax)
- ❌ `states="state1,state2"` (deprecated)  
- ✅ `invisible="state not in ['state1', 'state2']"` (new syntax)

## Module Status
The timesheet_approval module should now upgrade successfully with proper Odoo 18 compatibility.

## Next Steps
1. **Try Module Upgrade Again**: The XML syntax error should be resolved
2. **Test Configuration UI**: Should load without view parsing errors
3. **Verify Conditional Display**: The standard hours threshold field should show/hide based on auto-approval setting

The Configuration UI is now fully compatible with Odoo 18 view standards.
