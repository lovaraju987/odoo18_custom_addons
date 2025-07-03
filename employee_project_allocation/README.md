# Employee Project Allocation Module

## Overview

The **Employee Project Allocation** module is ### 🔧 **Technical Implementation**

#### Models Extended
- **`project.project`**: Enhanced with project type classification and enforcement controls
- **`project.sale.line.employee.map`**: Core allocation management with progress tracking
- **`account.analytic.line`**: Smart timesheet validation with flexible rules

#### Key Fields Added

**Project Model (`project.project`)**:
- `project_type`: Selection field for project classification (billable/internal types)
- `enforce_allocation_limits`: Boolean to control strict validation for internal projects

**Employee Allocation Model (`project.sale.line.employee.map`)**:
- `allocation_percentage`: Float field for percentage allocation (0-100%)
- `allocated_hours`: Computed field showing total hours allocated to employee
- `logged_hours`: Computed field showing hours already logged by employee
- `remaining_hours`: Computed field showing remaining available hours
- `completion_percentage`: Computed field showing work completion progress
- `project_total_hours`: Related field showing total project budget
- `project_start_date`: Related field showing project start date
- `project_end_date`: Related field showing project deadline
- `project_manager`: Related field showing project manager
- `project_type`: Related field showing project type

#### Advanced Methods & Logic

**Auto-Classification System**:
- `_onchange_allow_billable()`: Automatically sets project type based on billable configuration
- Smart detection of billable vs. internal projects

**Smart Auto-Distribution**:
- `_auto_distribute_percentages()`: Intelligent allocation distribution
- Conflict detection and prevention logic
- Equal distribution with logged hours protection

**Comprehensive Validation**:
- `_check_total_allocation_percentage()`: Flexible 100% limit based on project type
- `_check_allocation_vs_logged_hours()`: Protection against allocation reduction
- `_check_project_allocation_limit()`: Intelligent timesheet validation
- `_check_daily_limit()`: Daily hour limit enforcement

**Progress Tracking**:
- `_compute_allocated_hours()`: Real-time allocation calculation
- `_compute_logged_hours()`: Dynamic logged hours tracking
- `_compute_remaining_hours()`: Available hours calculation
- `_compute_completion_percentage()`: Progress percentage computationdoo 18 addon that provides advanced project resource management capabilities with flexible validation rules. It allows project managers to define allocation percentages for employees on projects, track progress and completion, and enforces intelligent validation rules that adapt to different project types (billable vs. internal projects).

## 🌟 **Key Features**

### 🎯 **Core Allocation Management**

#### 1. **Employee Allocation System**
- **Allocation Percentage**: Define what percentage of a project each employee is allocated to
- **Allocated Hours**: Automatically calculated based on allocation percentage and total project hours
- **Logged Hours**: Real-time tracking of hours already logged by each employee
- **Remaining Hours**: Dynamic calculation of available hours for logging
- **Completion Percentage**: Visual progress tracking showing work completion status
- **Real-time Updates**: All metrics update automatically when percentages or project hours change

#### 2. **Smart Auto-Distribution**
- **Equal Distribution**: When employees are added to a project, allocations are automatically distributed equally
- **Conflict Detection**: Prevents auto-distribution when existing logged hours would conflict with equal sharing
- **Manual Override**: Managers can adjust percentages after auto-distribution
- **Intelligent Rebalancing**: When employees are removed, remaining allocations are redistributed

#### 3. **Project Type Management**
- **Automatic Classification**: Projects are automatically classified as "Client Billable" when billable features are enabled
- **Internal Project Types**: Support for various internal project categories:
  - Internal - Onboarding
  - Internal - Knowledge Transfer
  - Internal - Bench
  - Internal - Training
  - Internal - Other
- **Flexible Validation**: Different validation rules apply based on project type

#### 4. **Advanced Progress Tracking**
- **Project Information Display**: Shows project start/end dates, manager, and total hours
- **Visual Progress Indicators**: Color-coded completion percentages
- **Comprehensive Employee View**: Dedicated "My Project Allocations" menu for employees
- **Project Timeline Tracking**: Display of project deadlines and milestones

#### 5. **Intelligent Validation System**
- **Flexible 100% Rule**: Strict for billable projects, optional for internal projects
- **Logged Hours Protection**: Prevents reducing allocations below already logged work
- **Daily Hour Limits**: Configurable maximum hours per day per employee (default: 8 hours)
- **Project-Specific Limits**: Restricts timesheet entries based on individual allocation limits
- **Enforcement Controls**: Project-level setting to enable/disable strict allocation limits

### 📊 **Business Rules & Validation**

#### Flexible Allocation Constraints
1. **Project Type-Based Validation**: 
   - **Billable Projects**: Strict 100% allocation limit enforced
   - **Internal Projects**: Flexible allocation limits (can exceed 100% if needed)
   - **Configurable Enforcement**: Project-level "Enforce Allocation Limits" toggle for internal projects

2. **Protection Rules**:
   - **Minimum Allocation Protection**: Cannot reduce an employee's allocation below their already logged hours percentage
   - **Smart Conflict Detection**: Auto-distribution only occurs when safe (no conflicts with existing work)

3. **Auto-Distribution Logic**: 
   - New employees get equal share of 100%
   - Existing allocations are rebalanced when employees are added/removed
   - System skips auto-distribution if conflicts detected with logged hours

#### Intelligent Timesheet Validation
1. **Allocation-Based Limits**: 
   - **Billable Projects**: Employees can only log hours up to their allocated percentage
   - **Internal Projects**: Flexible or strict limits based on project settings
   - **Real-time Validation**: Immediate feedback when limits are exceeded

2. **Daily Limits**: 
   - Maximum 8 hours per day per employee across all projects
   - Prevents overwork and ensures work-life balance
   - Configurable limit (can be adjusted in code)

3. **Smart Error Messages**: 
   - Clear, actionable error messages with specific numbers
   - Shows current vs. allowed allocations
   - Guidance on how to resolve conflicts

### 🎨 **User Experience Features**

#### Enhanced Project Form
- **Project Type Tab**: Dedicated tab for project classification and allocation settings
- **Auto-Classification**: Billable projects automatically tagged as "Client Billable"
- **Allocation Controls**: Easy access to enforcement settings for internal projects
- **Visual Allocation Display**: Clear view of all employee allocations and progress

#### Employee Self-Service
- **My Project Allocations Menu**: Dedicated view for employees to see all their project assignments
- **Comprehensive Information**: Shows allocation %, allocated hours, logged hours, remaining hours
- **Project Context**: Display of project manager, dates, deadlines, and project type
- **Progress Tracking**: Visual completion percentages with color coding
- **Real-time Updates**: All information updates in real-time as work is logged

#### Manager Dashboard
- **Allocation Overview**: Complete view of all employee allocations per project
- **Progress Monitoring**: Track completion percentages for all team members
- **Conflict Detection**: Visual indicators when allocations need attention
- **Flexible Controls**: Easy adjustment of allocation rules per project type

### 🔧 **Technical Implementation**

#### Models Extended
- **`project.sale.line.employee.map`**: Added allocation percentage and calculated allocated hours
- **`account.analytic.line`**: Enhanced with allocation and daily limit validations

#### Key Fields Added
- `allocation_percentage`: Float field for percentage allocation (0-100%)
- `allocated_hours`: Computed field showing total hours allocated to employee
- `logged_hours`: Computed field showing hours already logged by employee
- `remaining_hours`: Computed field showing remaining available hours

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

### 🚀 **Setting Up Project Allocations**

#### 1. **Project Classification**
   - Navigate to Project → Projects → Select a project
   - The "Project Type" is automatically set to "Client Billable" for billable projects
   - For internal projects, manually select the appropriate type:
     - Internal - Onboarding
     - Internal - Knowledge Transfer
     - Internal - Bench
     - Internal - Training
     - Internal - Other

#### 2. **Allocation Configuration**
   - Click on the "Project Type & Allocation" tab
   - For internal projects, toggle "Enforce Allocation Limits" as needed
   - Navigate to the "Invoicing" tab for employee assignments

#### 3. **Employee Assignment & Allocation**
   - In the "Employee Mapping" section, add employees to the project
   - The system automatically assigns equal percentages to all employees
   - Manually adjust the "Allocation %" for each employee as needed
   - View real-time updates in "Allocated Hours", "Logged Hours", and "Remaining Hours"
   - Monitor "Completion %" for progress tracking

#### 4. **Validation & Limits**
   - **Billable Projects**: Total allocation cannot exceed 100%
   - **Internal Projects**: Flexible limits based on "Enforce Allocation Limits" setting
   - System prevents reducing allocations below already logged hours
   - Clear error messages guide you through any conflicts

### 👥 **Employee Experience - My Project Allocations**

#### 1. **Accessing Your Allocations**
   - Go to Timesheets → My Project Allocations
   - View all projects you're allocated to in one comprehensive list

#### 2. **Information Dashboard**
   - **Project Details**: Name, manager, start/end dates, total hours
   - **Your Allocation**: Percentage and allocated hours
   - **Progress Tracking**: Logged hours, remaining hours, completion percentage
   - **Project Type**: See if it's billable or internal project
   - **Visual Indicators**: Color-coded progress bars and completion status

#### 3. **Progress Monitoring**
   - Track your completion percentage across all projects
   - Monitor remaining hours available for logging
   - See project deadlines and plan your work accordingly
   - Identify which projects need more attention

### ⏰ **Smart Timesheet Entry**

#### 1. **Normal Timesheet Logging**
   - Employees log time as usual through Timesheets
   - System validates against allocation limits automatically
   - Different rules apply based on project type (strict for billable, flexible for internal)

#### 2. **Intelligent Validation**
   - **Allocation Limits**: Can't exceed your allocated percentage of project hours
   - **Daily Limits**: Maximum 8 hours per day across all projects
   - **Real-time Feedback**: Immediate validation with helpful error messages

#### 3. **Error Guidance**
   - Clear messages show current usage vs. allowed limits
   - Specific recommendations for resolving allocation conflicts
   - Guidance on contacting project managers for allocation adjustments

## ⚙️ **Configuration Options**

### Project Type Settings
- **Automatic Classification**: Billable projects are auto-tagged as "Client Billable"
- **Manual Classification**: Internal projects can be manually categorized
- **Flexible Validation**: Choose strict or flexible validation per internal project

### Daily Hour Limits
The daily hour limit is currently set to 8 hours and is defined in the code. To modify:

```python
DAILY_LIMIT = 8.0  # Change this value in models/project_allocation.py
```

### Validation Rule Customization
- **Billable Projects**: Always enforce strict validation (100% limit, allocation-based timesheet limits)
- **Internal Projects**: Configurable via "Enforce Allocation Limits" checkbox
- **Daily Limits**: Applied consistently across all project types

## 📋 **Detailed Examples**

### Scenario 1: Billable Project Setup
```
Project: Client Website Development (100 hours total)
Project Type: Client Billable (automatically set)
Employees Added: John, Jane, Bob
Auto-Distribution: 33.33% each (33.33 hours each)
Validation: Strict 100% limit enforced
```

### Scenario 2: Internal Project with Flexible Rules
```
Project: Team Training (50 hours total)  
Project Type: Internal - Training (manually set)
Enforce Allocation Limits: Disabled
Employees: John 60%, Jane 40%, Bob 30% (130% total allowed)
Validation: Flexible allocation, daily limits still apply
```

### Scenario 3: Manual Adjustment with Validation
```
Project: Website Development (100 hours)
Initial: John 33.33%, Jane 33.33%, Bob 33.33%
Adjusted: John 50%, Jane 30%, Bob 20%
Result: All employees get updated allocated hours
System Check: Total = 100% ✓
```

### Scenario 4: Conflict Prevention
```
Project: Development Project (100 hours)
Current: John 40% (logged 35 hours), Jane 60%
Attempt: Reduce John to 30% (30 hours)
Result: Error - "Cannot reduce allocation below logged hours (35 hrs)"
Solution: Minimum allocation for John must be 35% (35 hours)
```

### Scenario 5: Smart Auto-Distribution with Conflicts
```
Project: Ongoing Project (100 hours)
Current: John 50% (logged 45 hours), Jane 50% (logged 10 hours)
Action: Add new employee Bob
Auto-Distribution: Skipped due to conflict
Reason: Equal distribution (33.33% each) would give John only 33.33 hours, but he's already logged 45
Solution: Manual adjustment required
```

## 🚨 **Error Messages & Troubleshooting**

### Allocation Validation Errors

#### Over 100% Allocation (Billable Projects)
```
Error: "Total allocation percentage for project 'Website Development' cannot exceed 100%. Current total: 110.0%"
Solution: Reduce individual allocations to total ≤ 100%
```

#### Below Logged Hours
```
Error: "Cannot reduce John Smith's allocation to 25.0% (25.00 hrs) on project 'Development'. 
Employee has already logged 30.00 hours (equivalent to 30.0% of project). 
Minimum allocation should be 30.0%."
Solution: Set allocation to at least the logged hours percentage
```

### Timesheet Entry Errors

#### Allocation Limit Exceeded
```
Error: "John Smith is allowed to log only 40.0% (40.00 hrs) on project 'Website Development'. 
Already logged: 42.00 hrs."
Solution: Request allocation increase from project manager or log to different project
```

#### Daily Limit Exceeded  
```
Error: "John Smith cannot log more than 8.0 hours on 2025-07-01. Attempted: 9.50 hrs."
Solution: Distribute hours across multiple days or reduce daily entry
```

### Common Resolution Steps

1. **Allocation Conflicts**
   - Check current logged hours vs. allocation
   - Adjust allocation percentages accordingly
   - Consider if project is billable (strict) vs. internal (flexible)

2. **Auto-Distribution Issues**
   - Review existing logged hours for all employees
   - Manually set allocations when auto-distribution is blocked
   - Ensure total allocation aligns with project type rules

3. **Timesheet Validation Problems**
   - Verify employee allocation on specific project
   - Check daily hour totals across all projects
   - Contact project manager for allocation adjustments if needed

## 🔐 **Security & Access Control**

### Access Rights
- **Project Users**: Can view and edit allocations for assigned projects
- **Project Managers**: Full access to all allocation features and project settings
- **Employees**: Can view their own allocations through "My Project Allocations" menu
- **System Administrators**: Complete control over module configuration and settings

### Data Integrity & Protection
- **Database-Level Validation**: All constraints run at the database level for data consistency
- **Real-time Validation**: Immediate feedback prevents invalid data entry
- **Logged Hours Protection**: Prevents accidental reduction of allocations below completed work
- **Audit Trail**: All allocation changes are tracked through Odoo's standard logging

## 🚀 **Performance & Technical Notes**

### Performance Optimizations
- **Computed Fields**: Not stored to ensure real-time accuracy while maintaining performance
- **Optimized Queries**: Validation queries are designed for efficiency
- **Selective Validation**: Constraints only run when relevant fields change
- **Smart Caching**: Related fields use Odoo's built-in caching mechanisms

### Customization Points
- **Configurable Daily Limits**: Can be made user-configurable through settings
- **Additional Project Types**: Easy to add new internal project categories
- **Custom Validation Rules**: Framework supports additional business rules
- **Alternative Auto-Distribution**: Smart distribution algorithms can be customized
- **Reporting Integration**: Fields designed for easy integration with custom reports

### Integration Capabilities
- **Native Odoo Integration**: Seamlessly works with existing project, timesheet, and billing modules
- **API Friendly**: All fields and methods accessible via Odoo's REST/XML-RPC APIs
- **Export/Import Ready**: Standard Odoo data management tools work out of the box
- **Multi-Company Support**: Designed to work in multi-company environments

## 📊 **Module Dependencies & Compatibility**

### Required Dependencies
```python
'depends': ['project', 'hr_timesheet', 'sale_timesheet']
```

### Optional Enhancements
- **Project Planning**: Enhanced with project start/end date fields
- **Sales Integration**: Automatic billable project detection
- **HR Integration**: Employee-based validation and progress tracking
- **Reporting**: Compatible with standard Odoo reporting tools

### Odoo Version Compatibility
- **Designed for**: Odoo 18.0
- **Tested with**: Latest Odoo 18.0 releases
- **Migration Path**: Clear upgrade path for future Odoo versions

## 📁 **Technical File Structure**
```
employee_project_allocation/
├── __init__.py                          # Module initialization
├── __manifest__.py                      # Module manifest and dependencies
├── models/
│   ├── __init__.py                     # Models initialization  
│   └── project_allocation.py           # Core business logic and validations
├── security/
│   └── ir.model.access.csv             # Access control rules
├── views/
│   ├── project_project_views.xml       # Enhanced project form views
│   └── employee_allocation_views.xml   # Employee allocation views and menus
└── README.md                           # Comprehensive documentation
```

### Key Classes and Methods Summary

#### `Project` (project.project)
- **Fields**: `project_type`, `enforce_allocation_limits`
- **Methods**: `_onchange_allow_billable()` - Auto-classification logic

#### `ProjectSaleLineEmployeeMap` (project.sale.line.employee.map)  
- **Core Fields**: `allocation_percentage`, `allocated_hours`, `logged_hours`, `remaining_hours`, `completion_percentage`
- **Related Fields**: `project_total_hours`, `project_start_date`, `project_end_date`, `project_manager`, `project_type`
- **Computation Methods**: `_compute_allocated_hours()`, `_compute_logged_hours()`, `_compute_remaining_hours()`, `_compute_completion_percentage()`
- **Auto-Distribution**: `_auto_distribute_percentages()` - Smart allocation distribution
- **Validation**: `_check_total_allocation_percentage()`, `_check_allocation_vs_logged_hours()`

#### `TimesheetLine` (account.analytic.line)
- **Validation Methods**: `_check_project_allocation_limit()`, `_check_daily_limit()`
- **Smart Logic**: Flexible validation based on project type and enforcement settings

## 📈 **Version History & Roadmap**

### Version 1.0 (Current)
- ✅ Core allocation management with percentage-based distribution
- ✅ Smart auto-distribution with conflict detection
- ✅ Flexible validation system (billable vs. internal projects)
- ✅ Comprehensive progress tracking and completion monitoring
- ✅ Employee self-service "My Project Allocations" view
- ✅ Project type classification with automatic billable detection
- ✅ Real-time validation with intelligent error messages
- ✅ Protection against allocation reduction below logged hours
- ✅ Daily hour limits with configurable enforcement
- ✅ Enhanced project form with dedicated allocation management tabs

### Future Enhancements (Roadmap)
- 📋 **Configurable Daily Limits**: Admin settings for daily hour limits
- 📋 **Advanced Reporting**: Allocation utilization and progress reports  
- 📋 **Mobile Optimization**: Enhanced mobile view for employee allocations
- 📋 **Notification System**: Alerts for allocation conflicts and deadline approaches
- 📋 **Resource Planning**: Integration with resource planning and capacity management
- 📋 **Time Tracking Analytics**: Advanced analytics for allocation effectiveness
- 📋 **Multi-Project Views**: Cross-project allocation and resource utilization views

## 🆘 **Support & Resources**

### Getting Help
- **Documentation**: This comprehensive README covers all features and use cases
- **Error Messages**: Self-explanatory error messages with actionable guidance
- **Debug Mode**: Odoo's debug mode provides additional technical information
- **Community**: Odoo community forums for general Odoo questions

### Best Practices
- **Regular Monitoring**: Review allocation percentages regularly as projects evolve
- **Clear Communication**: Ensure team members understand allocation limits and project types
- **Consistent Classification**: Maintain consistent project type classification
- **Proactive Adjustment**: Adjust allocations before conflicts arise with logged hours
- **Training**: Provide training on the employee self-service features

### Customization Support
- **Well-Documented Code**: Clear comments and documentation throughout the codebase
- **Modular Design**: Easy to extend with additional features
- **Standard Patterns**: Follows Odoo development best practices
- **Configuration Options**: Multiple points for customization without code changes

## 👨‍💻 **Author & License**

**Author**: OneTo7 Services  
**License**: LGPL-3  
**Version**: 1.0  
**Odoo Version**: 18.0  

---

*This module represents a comprehensive solution for project resource allocation management in Odoo 18, combining intelligent automation with flexible business rules to support both billable client work and internal project management needs.*
