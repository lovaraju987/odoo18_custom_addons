# Odoo 18 Context Variable Fix - active_id to id

## Issue Description

When upgrading to Odoo 18, the module installation failed with an error related to `active_id` not being accessible in form view contexts. The error occurred because Odoo 18 has stricter validation for context variables in views.

## Error Details

```
Access Rights Inconsistency
This view may not work for all users: some users may have a combination of groups where the elements <field name="submission_ids"/> are displayed, but they depend on the field active_id that is not accessible.

- field "active_id" does not exist in model "kpi.report"
- element "<field name="submission_ids" context="{'default_kpi_id': active_id}"/>" is shown in the view
```

## Root Cause

In Odoo 18, when referencing the current record ID in form view contexts, the proper variable is `id` instead of `active_id`. The `active_id` variable is typically available in wizard/action contexts, but not in regular form views.

## Solution Applied

Replaced all instances of `active_id` with `id` in form view contexts:

### Files Modified:

1. **`views/kpi_views.xml`**:
   ```xml
   <!-- Before -->
   <field name="submission_ids" context="{'default_kpi_id': active_id}">
   
   <!-- After -->
   <field name="submission_ids" context="{'default_kpi_id': id}">
   ```

2. **`views/kpi_report_group.xml`**:
   ```xml
   <!-- Before -->
   <field name="kpi_ids" context="{'default_report_id': active_id}" mode="list,form">
   <field name="submission_ids" context="{'default_report_id': active_id}">
   <field name="group_submission_ids" context="{'default_report_id': active_id}">
   
   <!-- After -->
   <field name="kpi_ids" context="{'default_report_id': id}" mode="list,form">
   <field name="submission_ids" context="{'default_report_id': id}">
   <field name="group_submission_ids" context="{'default_report_id': id}">
   ```

## Context Variable Usage Guide

### In Form Views:
- ✅ Use `id` to reference current record ID
- ✅ Use `uid` to reference current user ID
- ✅ Use `context_today()` for current date

### In Action Contexts:
- ✅ Use `active_id` for single record actions
- ✅ Use `active_ids` for multi-record actions
- ✅ Use `active_model` for the source model

### In Wizards:
- ✅ Use `active_id` and `active_ids` from action context
- ✅ Access via `self.env.context.get('active_id')`

## Benefits of This Fix

1. **Odoo 18 Compatibility**: Resolves installation errors in Odoo 18
2. **Improved Validation**: Passes Odoo's stricter context validation
3. **Consistent Behavior**: Ensures reliable context variable access
4. **Future-Proof**: Aligns with Odoo's recommended practices

## Testing Verification

After applying this fix, verify that:

1. ✅ Module installs without errors
2. ✅ Form views open correctly
3. ✅ Related lists (One2many fields) display properly
4. ✅ Default values are set correctly when creating related records
5. ✅ Context is properly passed to child views

## Additional Notes

- This is a framework-level change in Odoo 18's context handling
- The fix maintains all existing functionality
- No data migration is required
- The change only affects view definitions, not business logic
