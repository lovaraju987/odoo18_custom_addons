# KPI Tracking Security & Validation Improvements

## Security Enhancements

### 1. Enhanced Record Rules
The current record rules are too restrictive and may prevent new record creation. We need to make them more flexible while maintaining security.

**Current Issues:**
- New KPI records fail because `assigned_user_ids` is empty during creation
- Department-based rules are too strict for cross-department collaboration
- No fallback for users without department assignments

**Recommended Changes:**
```xml
<!-- More flexible user rule -->
<record id="rule_kpi_user_own_kpis" model="ir.rule">
    <field name="name">User: Own KPIs or Group KPIs</field>
    <field name="model_id" ref="model_kpi_report"/>
    <field name="groups" eval="[(4, ref('kpi_tracking.group_kpi_user'))]"/>
    <field name="domain_force">
      ['|', '|', '|',
        ('assigned_user_ids', 'in', [user.id]),
        ('report_id.assigned_employee_ids.user_id', '=', user.id),
        ('create_uid', '=', user.id),
        ('assigned_user_ids', '=', False)  # Allow access to unassigned KPIs
      ]
    </field>
</record>
```

### 2. Method-Level Security
Add proper permission checks in critical methods:

```python
def action_manual_refresh_kpi(self):
    """Enhanced with permission checks"""
    if not self.env.user.has_group('kpi_tracking.group_kpi_manager'):
        if self.env.user.id not in self.assigned_user_ids.ids:
            raise UserError("You can only update KPIs assigned to you.")
    
    # Rest of the method...
```

### 3. Input Validation
Add comprehensive validation for formula and domain fields:

```python
@api.constrains('formula_field', 'source_domain')
def _validate_formula_security(self):
    """Validate formula for security risks"""
    dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file']
    
    for rec in self:
        if rec.formula_field:
            formula_lower = rec.formula_field.lower()
            for keyword in dangerous_keywords:
                if keyword in formula_lower:
                    raise ValidationError(f"Formula contains dangerous keyword: {keyword}")
```

## Performance Optimizations

### 1. Database Indexes
Add indexes for frequently queried fields:

```sql
CREATE INDEX idx_kpi_report_department ON kpi_report(department);
CREATE INDEX idx_kpi_report_last_submitted ON kpi_report(last_submitted);
CREATE INDEX idx_kpi_submission_date ON kpi_report_submission(date);
```

### 2. Batch Processing
Optimize the scheduled update method:

```python
@api.model
def scheduled_update_kpis_batch(self):
    """Batch processing version for better performance"""
    batch_size = 50
    auto_kpis = self.search([('kpi_type', '=', 'auto')])
    
    for i in range(0, len(auto_kpis), batch_size):
        batch = auto_kpis[i:i + batch_size]
        self._process_kpi_batch(batch)
        self.env.cr.commit()  # Commit after each batch
```

### 3. Query Optimization
Use search_read instead of search + field access:

```python
def get_kpi_summary(self):
    """Optimized method to get KPI summary"""
    return self.search_read(
        [('kpi_type', '=', 'auto')],
        ['name', 'value', 'target_value', 'achievement_percent', 'department']
    )
```

## Data Integrity Improvements

### 1. Database Constraints
Add constraints in the model:

```python
_sql_constraints = [
    ('target_value_positive', 'CHECK(target_value > 0)', 'Target value must be positive'),
    ('unique_kpi_user_date', 'UNIQUE(kpi_id, user_id, date(date))', 'Only one submission per user per day'),
    ('achievement_percent_range', 'CHECK(achievement_percent >= 0)', 'Achievement percent cannot be negative')
]
```

### 2. Enhanced Validation
Add comprehensive field validation:

```python
@api.constrains('target_value', 'target_type')
def _validate_target_value(self):
    for rec in self:
        if rec.target_type == 'percent' and rec.target_value > 100:
            raise ValidationError("Percentage target cannot exceed 100%")
        if rec.target_type == 'boolean' and rec.target_value not in [0, 1]:
            raise ValidationError("Boolean target must be 0 or 1")
```

## User Experience Enhancements

### 1. Better Error Messages
Provide specific error messages:

```python
def _validate_formula_syntax(self):
    """Provide specific error messages for formula validation"""
    try:
        # Validation logic
        pass
    except SyntaxError as e:
        raise ValidationError(f"Formula syntax error at position {e.offset}: {e.msg}")
    except NameError as e:
        raise ValidationError(f"Unknown variable in formula: {e}")
```

### 2. Client-side Validation
Add JavaScript validation for immediate feedback:

```javascript
// In view file
<field name="formula_field" widget="text" 
       options="{'validate_formula': true}"/>
```

### 3. Contextual Help
Add helpful tooltips and documentation:

```xml
<field name="formula_field" 
       help="Available variables: count_a, count_b, records, assigned_user, today"/>
```

## Monitoring & Logging

### 1. Performance Monitoring
Add performance tracking:

```python
import time
from odoo.tools import log

def scheduled_update_kpis(self):
    start_time = time.time()
    try:
        # Processing logic
        pass
    finally:
        duration = time.time() - start_time
        log.info(f"KPI update completed in {duration:.2f} seconds")
```

### 2. Audit Trail
Enhanced audit logging:

```python
@api.model
def create(self, vals):
    result = super().create(vals)
    self.env['kpi.audit.log'].create({
        'action': 'create',
        'kpi_id': result.id,
        'user_id': self.env.user.id,
        'details': f"KPI '{result.name}' created"
    })
    return result
```

## Implementation Priority

1. **High Priority (Week 1)**
   - Fix security rules for new record creation
   - Add method-level permission checks
   - Implement basic input validation

2. **Medium Priority (Week 2)**
   - Add database indexes
   - Implement batch processing
   - Add data integrity constraints

3. **Low Priority (Week 3)**
   - Add client-side validation
   - Implement audit logging
   - Add performance monitoring

This comprehensive improvement plan will significantly enhance the security, performance, and user experience of the KPI tracking module.
