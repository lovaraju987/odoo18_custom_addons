# KPI Form Editability Fix

## Issue
After the Odoo 18 migration, users reported that KPI creation and edit forms were not editable. All fields appeared as read-only, preventing users from creating or modifying KPIs.

## Root Cause
The issue was caused by restrictive permission logic in the `is_admin` computed field in `models/kpi_report.py`. The field only checked for `group_kpi_admin` membership, but the access rights were configured to allow both admin and manager users to have write permissions.

### Original Code
```python
@api.depends()
def _compute_is_admin(self):
    for rec in self:
        rec.is_admin = self.env.user.has_group('kpi_tracking.group_kpi_admin')
```

### Form Field Restrictions
All main form fields had `readonly="not is_admin"` which meant only admin users could edit them.

## Solution

### 1. Updated is_admin Computed Field
Modified the `_compute_is_admin` method to include both admin and manager groups:

```python
@api.depends()
def _compute_is_admin(self):
    for rec in self:
        # Allow both admin and manager users to edit KPIs
        rec.is_admin = (self.env.user.has_group('kpi_tracking.group_kpi_admin') or 
                       self.env.user.has_group('kpi_tracking.group_kpi_manager'))
```

### 2. Updated Field Label
Changed the field description to be more accurate:
```python
is_admin = fields.Boolean(string="Can Edit KPI", compute="_compute_is_admin", store=False)
```

### 3. Fixed Access Rights
Updated `security/ir.model.access.csv` to give managers create permissions:
```csv
# Before
access_kpi_report_manager,kpi.report.manager,model_kpi_report,kpi_tracking.group_kpi_manager,1,1,0,0

# After  
access_kpi_report_manager,kpi.report.manager,model_kpi_report,kpi_tracking.group_kpi_manager,1,1,1,0
```

## User Groups and Permissions

| Group | Read | Write | Create | Delete | Can Edit Forms |
|-------|------|-------|--------|--------|----------------|
| KPI Admin | ✓ | ✓ | ✓ | ✓ | ✓ |
| KPI Manager | ✓ | ✓ | ✓ | ✗ | ✓ |
| KPI User | ✓ | ✗ | ✗ | ✗ | ✗ |

## Files Modified
- `models/kpi_report.py` - Updated `_compute_is_admin` method and field label
- `security/ir.model.access.csv` - Granted create permissions to managers

## Testing
1. Install/upgrade the module
2. Assign a user to the "KPI Manager" group
3. Login as that user
4. Verify that KPI forms are now editable
5. Test both creating new KPIs and editing existing ones

## Impact
- Admin users: No change - can still create/edit/delete KPIs
- Manager users: Can now create and edit KPIs (but not delete)
- Regular users: No change - still read-only access
