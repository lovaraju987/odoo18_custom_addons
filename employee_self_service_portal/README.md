# Employee Self Service Portal MLR

## Overview
This module provides a comprehensive Employee Self Service (ESS) portal for Odoo 18, allowing employees to manage their personal information, attendance, CRM activities, and expenses through the portal interface.

## Features

### 📋 Employee Profile Management
- **Personal Information**: Update work email, phone, birthday, gender, marital status
- **Professional Details**: Manage experience, skills, and certifications
- **Bank Information**: Maintain bank account details and IFSC codes
- **Identity Documents**: Track nationality, Emirates ID, and passport information

### 🕒 Attendance Management
- **Smart Check-in/Check-out**: Location-based attendance tracking with GPS coordinates
- **Attendance History**: View monthly attendance records with filtering options
- **Work Hours Calculation**: Automatic calculation of daily working hours
- **Location Tracking**: Record check-in and check-out locations

### 🎯 CRM Integration
- **Lead Management**: Create, edit, and delete CRM leads
- **Activity Scheduling**: Schedule and track follow-up activities
- **Communication Tracking**: Log notes and attach files to leads
- **Tag Management**: Dynamic tag creation and assignment
- **Pipeline Management**: Track leads through different stages

### 💰 Expense Management
- **Expense Submission**: Submit expenses with supporting attachments
- **Category Management**: Organize expenses by product categories
- **Status Tracking**: Monitor expense approval status
- **Expense History**: View and filter submitted expenses
- **Withdrawal Option**: Cancel submitted expenses when needed

### 📄 Payslip Management
- **Payslip Viewing**: View detailed payslip information with salary breakdown
- **Download Functionality**: Download payslips as PDF documents
- **Filter Options**: Filter payslips by status, year, and month
- **Salary Details**: View comprehensive salary components, deductions, and totals
- **Worked Days**: Track worked days and hours for each pay period

## Installation

1. Copy the module to your Odoo addons directory
2. Update the app list in Odoo
3. Install the "Employee Self Service Portal MLR" module
4. Configure employee portal users by linking them to hr.employee records

## Configuration

### Employee Setup
1. Go to **Employees** app
2. Open an employee record
3. Set the **Portal User** field to link the employee with a portal user
4. Ensure the portal user has appropriate access rights

### Security Configuration
The module automatically configures security rules to ensure:
- Portal users can only access their own employee records
- Attendance records are restricted to the logged-in user
- CRM leads are user-specific
- Expense records follow employee ownership

## Usage

### For Employees
1. Log in to the portal using your credentials
2. Navigate to **ESS Portal** from the main portal page
3. Access different sections:
   - **My Profile**: Update personal and professional information
   - **My Attendance**: Check-in/out and view attendance history
   - **My CRM**: Manage leads and customer interactions
   - **My Payslips**: View and download payslips
   - **Expenses**: Submit and track expense claims

### For Administrators
1. Ensure employees have portal user accounts
2. Configure expense product categories
3. Set up CRM stages and activity types
4. Monitor employee data through standard Odoo interfaces

## Technical Details

### Dependencies
- `portal`: Core portal functionality
- `hr`: Human resources management
- `hr_attendance`: Attendance tracking
- `om_hr_payroll`: Payroll integration
- `hr_holidays`: Leave management integration

### Model Extensions
- **hr.employee**: Extended with additional fields for portal use
- **hr.attendance**: Enhanced with location tracking capabilities

### Routes
- `/my/ess`: Main ESS dashboard
- `/my/employee`: Employee profile management
- `/my/employee/attendance`: Attendance tracking
- `/my/employee/crm`: CRM lead management
- `/my/employee/payslips`: Payslip viewing and downloading
- `/my/employee/expenses`: Expense management

## Customization

The module is designed to be easily extensible. Common customizations include:
- Adding new employee profile fields
- Customizing attendance tracking rules
- Extending CRM functionality
- Adding new expense categories

## Support

For support and customization requests, contact:
- **Author**: Lovaraju Mylapalli
- **Website**: https://www.mlr.com

## License
LGPL-3

## Version History
- **v1.0**: Initial release with core ESS functionality
