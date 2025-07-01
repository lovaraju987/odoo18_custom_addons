# Employee Project Allocation Module

## Overview

The **Employee Project Allocation** module is a comprehensive Odoo 18 addon that provides advanced project resource management capabilities. It allows project managers to define allocation percentages for employees on projects, automatically calculates allocated hours, and enforces strict validation rules for both project allocations and timesheet entries.

## Features

### 🎯 **Core Functionality**

#### 1. **Employee Allocation Management**
- **Allocation Percentage**: Define what percentage of a project each employee is allocated to
- **Allocated Hours**: Automatically calculated based on allocation percentage and total project hours
- **Real-time Updates**: Allocation hours update automatically when percentages or project hours change

#### 2. **Smart Auto-Distribution**
- **Equal Distribution**: When employees are added to a project, allocations are automatically distributed equally
- **Conflict Detection**: Prevents auto-distribution when existing logged hours would conflict
- **Manual Override**: Managers can adjust percentages after auto-distribution

#### 3. **Advanced Validation System**
- **100% Allocation Limit**: Ensures total allocation across all employees never exceeds 100%
- **Logged Hours Protection**: Prevents reducing allocations below already logged work
- **Daily Hour Limits**: Enforces maximum 8 hours per day per employee
- **Project Hour Limits**: Restricts timesheet entries based on individual allocation limits

### 📊 **Business Rules**

#### Allocation Constraints
1. **Total Allocation Limit**: Sum of all employee allocations on a project cannot exceed 100%
2. **Minimum Allocation Protection**: Cannot reduce an employee's allocation below their already logged hours percentage
3. **Auto-Distribution Logic**: New employees get equal share, but only if no conflicts with existing logged hours

#### Timesheet Validation
1. **Allocation-Based Limits**: Employees can only log hours up to their allocated percentage of total project hours
2. **Daily Limits**: Maximum 8 hours per day per employee across all projects
3. **Real-time Validation**: Constraints are enforced when creating or updating timesheet entries

### 🔧 **Technical Implementation**

#### Models Extended
- **`project.sale.line.employee.map`**: Added allocation percentage and calculated allocated hours
- **`account.analytic.line`**: Enhanced with allocation and daily limit validations

#### Key Fields Added
- `allocation_percentage`: Float field for percentage allocation (0-100%)
- `allocated_hours`: Computed field showing total hours allocated to employee

#### Validation Methods
- `_check_total_allocation_percentage()`: Ensures project total ≤ 100%
- `_check_allocation_vs_logged_hours()`: Protects against reduction below logged hours
- `_check_project_allocation_limit()`: Validates timesheet entries against allocations
- `_check_daily_limit()`: Enforces 8-hour daily maximum

## Installation

### Prerequisites
- Odoo 18.0
- Required modules: `project`, `hr_timesheet`, `sale_timesheet`

### Installation Steps
1. Copy the `employee_project_allocation` folder to your Odoo addons directory
2. Update the app list in Odoo
3. Install the "Employee Project Allocation" module

## Usage

### Setting Up Project Allocations

1. **Navigate to Project**
   - Go to Project → Projects → Select a project
   - Click on the "Invoicing" tab

2. **Assign Employees**
   - In the "Employee Mapping" section, add employees to the project
   - The system automatically assigns equal percentages to all employees

3. **Adjust Allocations**
   - Manually adjust the "Allocation %" for each employee as needed
   - The "Allocated Hours" column updates automatically
   - Ensure total allocation doesn't exceed 100%

### Timesheet Entry

1. **Normal Timesheet Entry**
   - Employees log time as usual through Timesheets
   - System validates against allocation and daily limits automatically

2. **Validation Messages**
   - Clear error messages guide users when limits are exceeded
   - Messages show current usage vs. allowed limits

## Configuration

### Daily Hour Limit
The daily hour limit is currently set to 8 hours and is defined in the code. To modify:

```python
DAILY_LIMIT = 8.0  # Change this value in models/project_allocation.py
```

### Validation Rules
All validation rules are enforced automatically and cannot be disabled without code modification.

## Examples

### Scenario 1: Initial Project Setup
```
Project: Website Development (100 hours total)
Employees Added: John, Jane, Bob
Auto-Distribution: 33.33% each (33.33 hours each)
```

### Scenario 2: Manual Adjustment
```
Project: Website Development (100 hours)
Initial: John 33.33%, Jane 33.33%, Bob 33.33%
Adjusted: John 50%, Jane 30%, Bob 20%
Result: All employees get updated allocated hours
```

### Scenario 3: Conflict Prevention
```
Project: Website Development (100 hours)
Current: John 40% (logged 35 hours), Jane 60%
Attempt: Reduce John to 30%
Result: Error - "Cannot reduce allocation below logged hours"
```

## Error Messages

### Allocation Errors
- **Over 100% allocation**: "Total allocation percentage cannot exceed 100%"
- **Below logged hours**: "Cannot reduce allocation below already logged hours"

### Timesheet Errors
- **Allocation exceeded**: "Employee allowed only X% on this project"
- **Daily limit exceeded**: "Cannot log more than 8 hours on this date"

## Troubleshooting

### Common Issues

1. **Cannot Add Employee to Project**
   - Ensure the project has employees assigned in the Invoicing tab
   - Check that the sale_timesheet module is installed

2. **Allocation Percentage Not Saving**
   - Verify total allocation doesn't exceed 100%
   - Check that the new percentage isn't below already logged hours

3. **Timesheet Entry Blocked**
   - Check employee's allocation percentage and remaining hours
   - Verify daily limit hasn't been exceeded

### Debug Tips
- Check the project's "Allocated Hours" field value
- Verify employee assignments in the Invoicing tab
- Review existing timesheet entries for the employee/project

## Security

### Access Rights
- **Project Users**: Can view and edit allocations
- **Project Managers**: Full access to all allocation features
- **Employees**: Can view their own allocations (through timesheet interface)

### Data Integrity
- All validations run at the database level
- Constraints prevent data inconsistencies
- Real-time validation provides immediate feedback

## Technical Notes

### Performance Considerations
- Computed fields are not stored to ensure real-time accuracy
- Validation queries are optimized for performance
- Constraints only run when relevant fields change

### Customization Points
- Daily hour limit can be made configurable
- Additional validation rules can be added
- Custom allocation algorithms can be implemented

## Dependencies

```python
'depends': ['project', 'hr_timesheet', 'sale_timesheet']
```

## Technical Details

### Files Structure
```
employee_project_allocation/
├── __init__.py                     # Module initialization
├── __manifest__.py                 # Module manifest and dependencies
├── models/
│   ├── __init__.py                # Models initialization
│   └── project_allocation.py      # Core business logic and validations
├── security/
│   └── ir.model.access.csv        # Access control rules
└── views/
    └── project_project_views.xml   # UI modifications for project form
```

### Key Classes and Methods

#### ProjectSaleLineEmployeeMap
- `allocation_percentage`: Main allocation field
- `allocated_hours`: Computed field for allocated hours
- `_compute_allocated_hours()`: Calculates allocated hours
- `_auto_distribute_percentages()`: Smart auto-distribution logic
- `_check_total_allocation_percentage()`: Validates 100% limit
- `_check_allocation_vs_logged_hours()`: Protects logged hours

#### TimesheetLine
- `_check_project_allocation_limit()`: Validates timesheet against allocations
- `_check_daily_limit()`: Enforces daily hour limits

## Version History

### Version 1.0
- Initial release with core allocation functionality
- Automatic percentage distribution for new employees
- Comprehensive validation system
- Integration with existing project invoicing tab
- Timesheet restriction based on allocations
- Daily hour limit enforcement
- Protection against allocation reduction below logged hours

## Customization Options

### Make Daily Limit Configurable
The daily limit (currently 8 hours) can be made configurable by adding a settings model:

```python
# Add to settings
daily_timesheet_limit = fields.Float(
    string="Daily Timesheet Limit", 
    default=8.0
)
```

### Add Remaining Hours Display
Add computed fields to show remaining allocated hours:

```python
remaining_hours = fields.Float(
    string="Remaining Hours",
    compute="_compute_remaining_hours"
)
```

### Warning Instead of Blocking
Replace `@api.constrains` with `@api.onchange` for warnings instead of hard blocks.

## Support

For technical support or feature requests:
- Review the comprehensive validation error messages
- Check the module's constraints and business logic
- Test scenarios in a development environment first

## Author
OneTo7 Services

## License
LGPL-3
