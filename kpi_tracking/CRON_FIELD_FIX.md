# Odoo 18 Cron Job Field Fix - numbercall Removal

## Issue Description

When upgrading to Odoo 18, the module installation failed because the `numbercall` field in `ir.cron` model has been deprecated and removed. This caused a ValueError during module installation.

## Error Details

```
ValueError: Invalid field 'numbercall' on model 'ir.cron'
```

The error occurred while parsing cron job records that used the deprecated `numbercall` field.

## Root Cause

In Odoo 18, the `numbercall` field has been removed from the `ir.cron` model as part of framework cleanup and modernization. This field was used to control how many times a cron job should execute before being deactivated.

## Solution Applied

Removed the `numbercall` field from all cron job definitions in the module:

### Files Modified:

1. **`views/kpi_views.xml`** - Auto Refresh KPI Reports cron:
   ```xml
   <!-- Before -->
   <record id="ir_cron_kpi_auto_refresh" model="ir.cron">
       <field name="name">Auto Refresh KPI Reports</field>
       <field name="model_id" ref="model_kpi_report"/>
       <field name="state">code</field>
       <field name="code">model.scheduled_update_kpis()</field>
       <field name="interval_number">1</field>
       <field name="interval_type">days</field>
       <field name="numbercall">-1</field>  <!-- REMOVED -->
       <field name="active">True</field>
   </record>
   
   <!-- After -->
   <record id="ir_cron_kpi_auto_refresh" model="ir.cron">
       <field name="name">Auto Refresh KPI Reports</field>
       <field name="model_id" ref="model_kpi_report"/>
       <field name="state">code</field>
       <field name="code">model.scheduled_update_kpis()</field>
       <field name="interval_number">1</field>
       <field name="interval_type">days</field>
       <field name="active">True</field>
   </record>
   ```

2. **`data/cron.xml`** - Manual KPI Reminder cron:
   ```xml
   <!-- Before -->
   <record id="ir_cron_kpi_reminder_manual" model="ir.cron">
       <field name="name">Reminder: Manual KPI Submission</field>
       <field name="model_id" ref="model_kpi_report"/>
       <field name="state">code</field>
       <field name="code">model.send_manual_kpi_reminders()</field>
       <field name="interval_number">1</field>
       <field name="interval_type">days</field>
       <field name="numbercall">-1</field>  <!-- REMOVED -->
       <field name="active">True</field>
   </record>
   
   <!-- After -->
   <record id="ir_cron_kpi_reminder_manual" model="ir.cron">
       <field name="name">Reminder: Manual KPI Submission</field>
       <field name="model_id" ref="model_kpi_report"/>
       <field name="state">code</field>
       <field name="code">model.send_manual_kpi_reminders()</field>
       <field name="interval_number">1</field>
       <field name="interval_type">days</field>
       <field name="active">True</field>
   </record>
   ```

## Impact on Functionality

### Previous Behavior (Odoo 17 with numbercall):
- `numbercall="-1"` meant the cron job would run indefinitely
- The field controlled execution count limits

### New Behavior (Odoo 18 without numbercall):
- **No Functional Change**: Cron jobs still run indefinitely by default
- **Simplified Configuration**: Less fields to configure
- **Modern Framework**: Aligns with Odoo 18's streamlined cron system

## Migration Guide for Other Modules

If you have other modules with cron jobs, follow this pattern:

### ✅ Keep These Fields:
- `name` - Display name for the cron job
- `model_id` - Reference to the model containing the method
- `state` - Should be "code" for Python method execution
- `code` - The Python code/method to execute
- `interval_number` - How often to run (number)
- `interval_type` - Time unit (minutes, hours, days, weeks, months)
- `active` - Whether the cron job is enabled

### ❌ Remove These Deprecated Fields:
- `numbercall` - No longer supported in Odoo 18
- Any other deprecated cron fields

### Example Migration:
```xml
<!-- Odoo 17 and earlier -->
<record id="my_cron_job" model="ir.cron">
    <field name="name">My Scheduled Task</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">model.my_method()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">hours</field>
    <field name="numbercall">-1</field>  <!-- Remove this -->
    <field name="active">True</field>
</record>

<!-- Odoo 18 -->
<record id="my_cron_job" model="ir.cron">
    <field name="name">My Scheduled Task</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">model.my_method()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">hours</field>
    <field name="active">True</field>
</record>
```

## Benefits of This Fix

1. **Odoo 18 Compatibility**: Resolves installation errors
2. **Future-Proof**: Aligns with current framework standards
3. **Simplified Configuration**: Fewer fields to manage
4. **Maintained Functionality**: All cron jobs work exactly as before

## Testing Verification

After applying this fix, verify that:

1. ✅ Module installs without cron-related errors
2. ✅ Both cron jobs are created and visible in Settings > Technical > Automation > Scheduled Actions
3. ✅ Cron jobs execute on schedule:
   - **Auto Refresh KPI Reports**: Runs daily to update automatic KPIs
   - **Manual KPI Reminders**: Sends daily reminder emails for manual KPIs
4. ✅ Cron jobs can be manually triggered from the UI
5. ✅ Log entries show successful execution

## Additional Notes

- This change is purely structural - no business logic is affected
- Existing cron job schedules will continue working as expected
- The removal of `numbercall` simplifies cron job management
- All KPI tracking automation continues to function normally
