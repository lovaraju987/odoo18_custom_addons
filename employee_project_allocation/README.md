# Employee Project Allocation Module

## Overview
This Odoo 18 module adds allocation percentage per employee in a project's invoicing tab and restricts employee timesheets based on project allocation percentage and daily hour limits.

## Features

### ✅ Project Allocation Management
- Adds **allocation percentage** field for each employee in project's invoicing tab
- Allows project managers to define what percentage of a project is allocated to each employee

### ✅ Timesheet Restrictions
1. **Project Allocation Limit**: Prevents employees from logging more hours than their allocated project percentage
2. **Daily Hour Limit**: Prevents employees from logging more than 9 hours per day across all projects

## How It Works

### Project Setup
1. Go to any project → Invoicing tab
2. Add employees to the project
3. Set allocation percentage for each employee

### Example
**Project A** with 200 allocated hours:
- Employee 1 → 40% allocation → allowed 80 hours total
- Employee 2 → 60% allocation → allowed 120 hours total

### Validation Rules
The system will:
- ✅ Prevent Employee 1 from logging more than 80 hours total on Project A
- ✅ Prevent any employee from logging over 9 hours in a single day across all projects
- ✅ Show clear error messages when limits are exceeded

## Installation
1. Place this module in your Odoo addons directory
2. Update the app list in Odoo
3. Install the "Employee Project Allocation" module

## Dependencies
- `project` - Core project management
- `hr_timesheet` - Timesheet functionality

## Technical Details

### Models Extended
- `project.employee.allocation` - New model for employee project allocations
- `project.project` - Adds employee_allocation_ids field
- `account.analytic.line` - Adds validation constraints

### Files Structure
```
employee_project_allocation/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── project_allocation.py
├── security/
│   └── ir.model.access.csv
└── views/
    └── project_project_views.xml
```

## Customization Options

### Make Daily Limit Configurable
The daily limit (currently 9 hours) can be made configurable by adding a settings model.

### Show Remaining Hours
Add smart buttons or project fields to display remaining allocated hours per employee.

### Warning Instead of Blocking
Replace `@api.constrains` with `@api.onchange` to show warnings instead of hard blocks.

## Author
OneTo7 Services

## License
LGPL-3
