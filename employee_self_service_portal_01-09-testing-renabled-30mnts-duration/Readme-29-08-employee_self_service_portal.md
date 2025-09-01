# Employee Self Service Portal (ESS) - MLR

**Module Name:** Employee Self Service Portal MLR  
**Version:** 18.1.5  
**Category:** Human Resources  
**Author:** Lovaraju Mylapalli  
**Website:** https://www.mlr.com  
**License:** LGPL-3  

## Overview

The **Employee Self Service Portal (ESS) MLR** transforms Odoo's standard portal into a comprehensive employee self-service platform. This solution empowers TechCarrot's workforce to manage their HR-related activities through a dedicated, user-friendly interface accessible 24/7 from any device.

Built as a cost-effective alternative to expensive third-party ESS modules, this custom solution provides a complete suite of features including profile management, attendance tracking, CRM opportunity management, expense processing, payslip access, and advanced security controls—all while maintaining seamless integration with existing Odoo workflows.

The portal bridges the gap between employees and HR systems, reducing administrative overhead and enhancing employee engagement by providing instant access to personal information and services.

## Key Features

### 👤 **Advanced Profile Management**
- **Comprehensive Personal Data:** Complete profile editing with contact details, demographics, and professional information
- **Multi-Section Interface:** Organized access to personal, professional, certification, and banking details
- **Secure Banking Information:** Protected banking details for payroll processing
- **Document Management:** Upload and manage personal documents and certifications
- **Real-time Updates:** Instant profile changes without workflow delays

### ⏰ **Timezone-Aware Attendance Tracking**
- **Local Time Check-In/Out:** One-click attendance recording in employee's local timezone
- **GPS Location Integration:** Automatic capture of location coordinates for remote work verification
- **Visual Calendar:** Monthly attendance views with clear status indicators
- **Comprehensive History:** Complete attendance records with filtering options
- **Auto-Checkout Protection:** Scheduled process to prevent forgotten checkouts

### 💼 **Multi-Company CRM Portal**
- **Lead Creation & Management:** Create and manage sales opportunities directly from the portal
- **Dynamic Customer Creation:** Create new contacts and companies on-the-fly during opportunity creation
- **TechCarrot CRM Integration:** Full support for custom fields from techcarrot_crm_mlr module
- **Activity & Notes Management:** Schedule activities and maintain communication logs
- **Sales Pipeline Visualization:** Track opportunity progress through customizable stages

### 💰 **Multi-Currency Expense Management**
- **Company-Specific Currency:** Automatic currency selection based on employee's assigned company
- **Dynamic Currency Display:** Real-time currency symbol updates throughout the interface
- **Receipt Management:** Upload and verify supporting documents for expenses
- **Approval Workflow Integration:** Monitor expense status through the approval process
- **Historical Tracking:** Complete expense history with filtering capabilities

### 📊 **Secure Payslip Access**
- **Protected Document Delivery:** Secure access to personal payslip records
- **Multi-Format Support:** View online or download as PDF
- **Historical Archive:** Access to complete payslip history
- **Detailed Breakdown:** View comprehensive earnings and deductions details
- **Multi-Company Support:** Proper handling of payslips across multiple companies

### 📱 **Responsive Dashboard**
- **Mobile-First Design:** Fully responsive interface optimized for all devices
- **Personalized Overview:** At-a-glance view of key metrics and activities
- **Quick Actions:** One-tap access to frequent operations
- **Status Indicators:** Real-time status visualization for attendance and requests
- **Cross-Module Integration:** Unified interface for all ESS functions

## Technical Architecture

### Core Components

#### Portal Controller System
The module is built around a centralized controller architecture that handles all portal routes, request processing, and security validations:

- **Main Controller:** Centralized entry point handling all employee portal routes
- **Authentication Layer:** Validates portal user permissions and employee-user mapping
- **Access Control:** Feature-level permission system through portal access groups
- **Timezone Management:** Intelligent timezone handling for accurate global attendance

#### Multi-Company Framework
The system implements comprehensive multi-company support with:

- **Dynamic Company Detection:** Automatic identification of employee's assigned company
- **Company-Specific Currency:** Proper currency symbol display throughout all interfaces
- **Data Isolation:** Strict company-based record filtering for security compliance
- **Cross-Company Support:** Ability to work with resources across multiple companies when authorized

#### Time & Currency Handling
Advanced time and currency management ensures consistent and accurate data representation:

- **Local Time Conversion:** Automatic conversion between UTC and employee's local timezone
- **Currency Symbol Management:** Dynamic currency symbol display based on company settings
- **Format Localization:** Proper number and date formatting based on locale settings
- **Timezone Detection:** Intelligent detection of user timezone with fallbacks

### Data Models & Relationships

#### Core Model Extensions
The module extends standard Odoo models with custom fields and methods:

- **hr.employee:** Extended with portal access fields and multi-company logic
- **hr.attendance:** Enhanced with location tracking and timezone awareness
- **crm.lead:** Customized for portal creation and employee-specific access
- **hr.expense:** Modified with multi-company and multi-currency support
- **hr.payslip:** Extended for secure portal access and display

#### Security Framework
Comprehensive security controls protect sensitive data while enabling self-service:

- **Record-Level Access:** Employees can only access their own records
- **Feature-Level Permissions:** Granular control through portal access groups
- **Cross-Model Protection:** Security rules across all integrated models
- **SQL Injection Prevention:** Secure parameter handling and input sanitization

### View Templates & User Interface

#### Modern Template Architecture
The interface is built on a modular template system for consistency and maintainability:

- **Base Portal Layout:** Enhanced Odoo portal layout with ESS-specific navigation
- **Section-Specific Templates:** Dedicated templates for each functional area
- **Responsive Components:** Mobile-optimized UI elements across all views
- **Enhanced Form Controls:** Advanced input components with validation

#### JavaScript Enhancements
Client-side functionality improves user experience and interface dynamics:

- **Location Services:** GPS integration for attendance location tracking
- **Dynamic Form Handling:** Real-time form validation and field updates
- **Interactive Components:** Enhanced dropdowns, date pickers, and selectors
- **Asynchronous Updates:** Background processing for smoother interactions

## Dependencies & Integration

### Core Dependencies
- **portal:** Foundation for portal functionality
- **hr:** Base employee management
- **hr_attendance:** Attendance tracking system
- **hr_payroll:** Payroll integration
- **hr_holidays:** Leave management integration
- **hr_expense:** Expense management system
- **techcarrot_crm_mlr:** Custom CRM fields and functionality

### Architecture Integration
The module seamlessly integrates with Odoo's core architecture:

- **ORM Compatibility:** Leverages Odoo's ORM for database operations
- **Access Rights System:** Utilizes Odoo's security model with extensions
- **Controller Framework:** Extends Odoo's HTTP controller system
- **Template Engine:** Built on Odoo's QWeb template system
- **Asset Pipeline:** Integrated with Odoo's asset bundling system

## Installation & Configuration

### Prerequisites
1. **Odoo 18.0** or higher with Enterprise features
2. **Portal module** properly configured
3. **Employee records** with valid user accounts
4. **TechCarrot CRM MLR** module for CRM functionality

### Installation Process
1. **Module Deployment:**
   - Place the module in your Odoo addons directory
   - Install required dependencies first
   - Install the employee_self_service_portal module via Apps menu

2. **Initial Configuration:**
   - Link employees to portal users (employee.user_id field)
   - Verify timezone settings for employees and companies
   - Configure expense categories and approval workflows
   - Set up CRM stages and opportunity types

3. **Security Setup:**
   - Configure portal access groups for specific features
   - Verify record rules are properly applied
   - Test data isolation between companies
   - Validate employee-specific access controls

## User Guide

### Employee Portal Access

#### First-Time Access
1. **Login Process:**
   - Use portal credentials to access Odoo
   - Navigate to My Account > Employee Dashboard
   - Complete initial profile setup if prompted

2. **Dashboard Navigation:**
   - Access profile, attendance, CRM, expenses, and payslips
   - View personal metrics and status indicators
   - Use quick links for common actions

### Using Key Features

#### Profile Management
1. **Updating Personal Information:**
   - Navigate to Profile section
   - Select appropriate tab (Personal, Experience, Certifications, Banking)
   - Update information and save changes
   - Verify updates are reflected throughout the system

2. **Document Management:**
   - Upload personal documents and certifications
   - Manage document visibility and sharing
   - Track document expiration dates

#### Attendance Management
1. **Daily Check-In/Out:**
   - From the Attendance page, click Check In/Out button
   - Allow location access when prompted for GPS coordinates
   - Verify check-in/out is recorded with correct local time
   - Review daily worked hours calculation

2. **Viewing Attendance History:**
   - Access the Attendance History section
   - Filter by date range or status
   - Export records if needed
   - Check for any attendance anomalies

#### CRM Opportunity Management
1. **Creating New Leads:**
   - Navigate to the CRM section
   - Click "Create New Lead" button
   - Fill required fields, including customer information
   - Use dynamic creation for new contacts or companies
   - Submit to create the opportunity

2. **Managing Opportunities:**
   - View personal opportunity pipeline
   - Update status and information as needed
   - Add notes and schedule activities
   - Track progress through sales stages

#### Expense Submission
1. **Submitting Expenses:**
   - Go to Expenses section
   - Click "Submit New Expense"
   - Select appropriate category and enter amount
   - Upload receipt documentation
   - Submit for approval

2. **Tracking Expense Status:**
   - View all submitted expenses
   - Filter by status, date, or category
   - Monitor approval progress
   - Check payment status when processed

#### Payslip Access
1. **Viewing Payslips:**
   - Navigate to Payslips section
   - Select period to view
   - Access detailed breakdown of earnings and deductions
   - Download PDF copies if needed

## Administrator Guide

### System Configuration

#### Portal Access Management
- **User-Employee Mapping:**
  - Ensure all portal users have corresponding employee records
  - Configure the user_id field on hr.employee to link to portal users
  - Verify access rights and record rules

- **Feature Activation:**
  - Configure available features through portal access groups
  - Set company-specific settings for multi-company environments
  - Manage default values and workflows

#### Security Administration
- **Access Control:**
  - Review and update security groups as needed
  - Monitor access logs for unusual activity
  - Validate data isolation between companies

- **Permission Management:**
  - Configure granular permissions through portal access groups
  - Set record-level access controls
  - Manage form view field access

### Troubleshooting

#### Common Issues
- **Profile Access Problems:**
  - Verify employee.user_id mapping is correct
  - Check portal user has proper access rights
  - Validate employee record is active

- **Attendance Errors:**
  - Check timezone configuration for user and company
  - Verify location services are enabled in browser
  - Validate attendance rules configuration

- **CRM Functionality:**
  - Ensure techcarrot_crm_mlr module is installed
  - Verify CRM access rights for portal user
  - Check stage configuration for opportunities

- **Currency Display Issues:**
  - Verify company currency settings
  - Check employee-company assignment
  - Validate template currency rendering

## Security Considerations

### Data Protection
- **Personal Information:**
  - Employee data is protected through record rules
  - Sensitive fields have additional access controls
  - Banking information has enhanced security

- **Access Controls:**
  - Portal users can only access their own records
  - Multi-company environments have strict data isolation
  - Session management includes security timeouts

### Compliance Features
- **Audit Trail:**
  - All critical actions are logged for accountability
  - Changes to sensitive data are tracked
  - Access attempts are monitored

- **Data Minimization:**
  - Only necessary information is displayed
  - Historical data can be archived or anonymized
  - Export controls limit data extraction

## Performance Optimization

### Efficient Data Access
- **Query Optimization:**
  - Efficient database queries with proper indexing
  - Limited record sets with appropriate domain filters
  - Batch processing for related records

- **Caching Strategy:**
  - View templates use fragment caching
  - Static assets are properly bundled and minified
  - Database query results are cached where appropriate

### Mobile Experience
- **Responsive Design:**
  - All interfaces adapt to mobile, tablet, and desktop
  - Touch-optimized controls for small screens
  - Reduced network usage for mobile connections

- **Progressive Enhancement:**
  - Core functionality works without JavaScript
  - Enhanced features with client-side processing
  - Offline capabilities where possible

## Future Roadmap

### Planned Enhancements
- **Leave Management Integration:**
  - Request and track time off through portal
  - Calendar integration with team visibility
  - Approval workflow with notifications

- **Training & Development:**
  - Access to training materials and courses
  - Skill assessment and certification tracking
  - Performance goal management

- **Team Collaboration:**
  - Enhanced communication tools
  - Team calendar and availability
  - Project and task visibility

### Technical Roadmap
- **API Extension:**
  - REST API for mobile app integration
  - Webhook support for external systems
  - Integration with third-party HR tools

- **Advanced Analytics:**
  - Enhanced reporting and visualization
  - Predictive analytics for HR metrics
  - Custom dashboards with drill-down capabilities

## Support & Resources

### Documentation
- Comprehensive user guides available in the company knowledge base
- Video tutorials for common workflows
- Frequently asked questions and troubleshooting tips

### Technical Support
- Internal support via service desk system
- Technical documentation for administrators
- Regular updates and security patches

## Changelog

### Version 18.1.5 (Current)
- ✅ Multi-company and multi-currency support throughout the portal
- ✅ Timezone-aware attendance with location tracking
- ✅ Enhanced CRM integration with dynamic customer creation
- ✅ Responsive design for all devices
- ✅ Comprehensive security framework with access groups
- ✅ Payslip access and document management

### Previous Versions
- 18.1.4: Initial expense management system
- 18.1.3: Basic CRM integration
- 18.1.2: Enhanced profile management
- 18.1.1: Core portal functionality and attendance

---

## Technical Appendix

### Module Structure
```
employee_self_service_portal/
├── controllers/
│   ├── access_helpers.py    # Access control helpers
│   ├── main.py             # Main portal controller
│   └── __init__.py
├── models/
│   ├── attendance.py       # Attendance model extensions
│   ├── crm_lead.py         # CRM opportunity extensions
│   ├── employee.py         # Employee model extensions
│   ├── hr_expense.py       # Expense model with multi-currency
│   ├── payslip.py          # Payslip access extensions
│   └── __init__.py
├── security/
│   ├── ir.model.access.csv # Access control records
│   ├── portal_access_groups.xml # Portal permission groups
│   └── portal_employee_security.xml # Record rules
├── views/
│   ├── Employee_details/   # Portal templates by section
│   ├── portal_layout.xml   # Base portal layout
│   ├── portal_ess_dashboard.xml # Dashboard template
│   └── menu.xml            # Portal menu structure
├── data/
│   ├── portal_data.xml     # Initial configuration data
│   ├── attendance_cron.xml # Scheduled tasks
│   └── expense_categories.xml # Default categories
├── static/
│   ├── description/        # Module metadata images
│   ├── src/                # Source JavaScript and CSS
│   └── lib/                # Third-party libraries
├── __init__.py
└── __manifest__.py         # Module definition
```

### Integration Points
- **Portal Module:** Extends portal.portal controller
- **HR Module:** Integrates with employee records
- **Attendance:** Extends check-in/out functionality
- **CRM:** Connects with opportunity management
- **Expenses:** Links to expense workflow
- **Payroll:** Securely accesses payslip data

### Developer Notes
- Template inheritance follows Odoo's QWeb extension pattern
- Controller methods use authentication decorators for security
- JavaScript components use Odoo's OWL framework
- Security follows least-privilege principle
- Multi-company design patterns throughout code
