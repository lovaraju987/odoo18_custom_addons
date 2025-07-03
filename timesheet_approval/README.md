# Timesheet Approval Workflow

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://github.com/odoo/odoo/tree/18.0)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL%203-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

A comprehensive timesheet approval workflow system designed specifically for **Odoo 18 Community Edition**. This module transforms the standard timesheet functionality into a powerful approval-based system with complete audit trails, manager oversight, and automated notifications.

## 🎯 Overview

The Timesheet Approval Workflow module addresses the critical need for timesheet oversight in organizations by providing:

- **Structured Approval Process**: Transform ad-hoc timesheet submissions into a formal approval workflow
- **Manager Accountability**: Designated managers review and approve team timesheets before processing
- **Audit Compliance**: Complete history of all timesheet submissions, approvals, and modifications
- **Operational Efficiency**: Batch operations and automated notifications reduce administrative overhead
- **Integration Ready**: Seamlessly works with existing Odoo modules and third-party project management tools

## 🚀 Key Features

### 📋 Workflow Management
- **4-State Workflow**: `Draft` → `Submitted` → `Approved` / `Rejected`
- **Smart State Transitions**: Automatic state management with validation rules
- **Flexible Approval Hierarchy**: Support for multiple approval levels and delegation
- **Batch Processing**: Approve or reject multiple timesheet submissions simultaneously
- **Deadline Management**: Configurable submission and approval deadlines

### 👥 User Experience
- **Role-Based Dashboards**: Customized views for employees, managers, and HR personnel
- **Intuitive Interfaces**: Clean, modern UI following Odoo 18 design patterns
- **Mobile Responsive**: Full functionality on mobile devices for on-the-go approvals
- **Quick Actions**: One-click approval/rejection buttons with comment support
- **Advanced Filtering**: Comprehensive search and filter options by employee, project, date, status

### 🔔 Communication & Notifications
- **Automated Email Notifications**: 
  - Submission confirmations to employees
  - Approval requests to managers
  - Status updates to all stakeholders
- **Customizable Templates**: Branded email templates with company information
- **Real-time Alerts**: In-app notifications for urgent approvals
- **Escalation Support**: Automatic reminders for overdue approvals

### 📊 Reporting & Analytics
- **Comprehensive Reports**: Detailed timesheet approval reports with export options
- **Performance Metrics**: Approval turnaround times and manager efficiency stats
- **Audit Trail**: Complete history of all approval actions with timestamps and comments
- **Dashboard Analytics**: Visual representations of approval status and trends

### 🔧 Integration Capabilities
- **Native Odoo Integration**: Works seamlessly with `hr_timesheet`, `project`, and `hr` modules
- **Employee Project Allocation**: Enhanced integration with project allocation constraints
- **Portal Access**: Client portal integration for project-based approvals
- **API Ready**: RESTful API endpoints for third-party integrations

### ⚙️ Configuration Management
- **Administrative UI**: Comprehensive configuration interface for system administrators
- **Dynamic Settings**: Real-time application of configuration changes across the system
- **Email Control**: Granular control over notification types and frequency
- **Workflow Customization**: Configurable approval rules, deadlines, and validation requirements
- **Auto-Approval**: Intelligent rules for automatic approval of standard timesheet entries
- **Batch Limits**: Performance management with configurable batch operation limits
- **Integration Toggles**: Enable/disable specific integration features as needed

## 📦 Installation

### Prerequisites
- **Odoo Version**: 18.0 Community Edition or Enterprise Edition
- **Python Version**: 3.10 or higher
- **Required Modules**: 
  - `base` (core)
  - `hr` (Human Resources)
  - `hr_timesheet` (Timesheets)
  - `project` (Project Management)
  - `mail` (Messaging)
  - `portal` (Portal Access)

### Installation Steps

1. **Download and Extract**:
   ```bash
   cd /path/to/odoo/addons/
   git clone <repository-url> timesheet_approval
   # OR extract from zip file
   ```

2. **Install via Odoo Interface**:
   - Navigate to `Apps` menu in Odoo
   - Remove the "Apps" filter to show all modules
   - Search for "Timesheet Approval Workflow"
   - Click `Install`

3. **Alternative: Install via Command Line**:
   ```bash
   ./odoo-bin -d <database_name> -i timesheet_approval --stop-after-init
   ```

### Post-Installation Configuration

1. **Access Rights Setup**:
   - Go to `Settings` → `Users & Companies` → `Users`
   - Assign appropriate groups to users:
     - `Timesheet Approval / User`: For employees who submit timesheets
     - `Timesheet Approval / Manager`: For managers who approve timesheets
     - `Timesheet Approval / Admin`: For HR personnel with full access

2. **Manager Assignment**:
   - Navigate to `Employees` → `Employees`
   - Set the `Manager` field for each employee
   - Configure approval hierarchy as needed

3. **Email Configuration**:
   - Ensure outgoing mail server is configured in `Settings` → `Technical` → `Email`
   - Test email notifications with sample submissions

4. **Module Configuration**:
   - Access the Configuration UI at `Timesheets` → `Timesheet Approvals` → `Configuration` → `Settings`
   - Configure deadlines, email notifications, and workflow settings
   - Test email settings using the built-in test functionality
   - Customize approval rules and batch limits according to your organization's needs

## 🎮 Usage Guide

### For Employees

#### Submitting Timesheets

1. **Create Timesheet Entries**:
   - Navigate to `Timesheets` → `My Timesheets`
   - Enter your daily time entries as usual
   - Ensure all required fields are completed

2. **Submit for Approval**:
   - Go to `Timesheets` → `My Timesheet Approvals`
   - Click `Create` to start a new submission
   - Select the date range for submission
   - Review timesheet entries in the preview
   - Click `Submit for Approval`

3. **Track Submission Status**:
   - Monitor status in `My Timesheet Approvals`
   - Receive email notifications for status changes
   - View manager comments for rejected submissions

4. **Handle Rejections**:
   - Review rejection comments from manager
   - Make necessary corrections to timesheet entries
   - Resubmit for approval using `Reset to Draft` → `Submit`

#### Dashboard View

- **Quick Stats**: View pending, approved, and rejected submissions
- **Recent Activity**: See latest approval actions and comments
- **Upcoming Deadlines**: Track submission deadlines
- **Action Items**: Direct links to pending tasks

### For Managers

#### Approval Process

1. **Review Pending Approvals**:
   - Navigate to `Timesheets` → `Team Timesheets`
   - Filter by `Submitted` status
   - Click on individual submissions to review details

2. **Individual Approval**:
   - Open timesheet submission
   - Review all time entries and project allocations
   - Add comments if necessary
   - Click `Approve` or `Reject`

3. **Batch Approval**:
   - Select multiple submissions using checkboxes
   - Click `Action` → `Batch Approval`
   - Choose approval action (Approve/Reject)
   - Add batch comments
   - Confirm action

4. **Approval Dashboard**:
   - Overview of team submission status
   - Pending approvals requiring attention
   - Performance metrics and turnaround times

#### Best Practices for Managers

- **Timely Reviews**: Aim to review submissions within 24-48 hours
- **Detailed Comments**: Provide specific feedback for rejections
- **Batch Processing**: Use batch approval for routine submissions
- **Regular Monitoring**: Check dashboard regularly for pending items

### For HR/Administrators

#### System Administration

1. **User Management**:
   - Assign appropriate access rights
   - Configure approval hierarchies
   - Manage delegation during absences

2. **Reporting and Analytics**:
   - Access comprehensive reports via `Timesheets` → `Reports`
   - Export data for external analysis
   - Monitor system performance and adoption

3. **Configuration Management**:
   - Access comprehensive configuration UI
   - Customize approval workflow settings
   - Configure email notifications and deadlines
   - Set up batch operation limits and auto-approval rules

## 🔧 Configuration Options

### Administrative Configuration UI

The module provides a comprehensive configuration interface accessible to system administrators at:
**Timesheets** → **Timesheet Approvals** → **Configuration** → **Settings**

#### Deadline Management
- **Submission Deadline**: Configure how many days employees have to submit timesheets after period end
- **Approval Deadline**: Set the number of days managers have to approve submitted timesheets
- **Auto-Submission**: Enable automatic timesheet submission when deadlines approach

#### Email Notification Control
- **Submission Notifications**: Toggle email alerts when timesheets are submitted
- **Approval Notifications**: Control email alerts for approval/rejection actions  
- **Reminder Notifications**: Enable/disable reminder emails for pending actions
- **Reminder Frequency**: Configure how often reminder emails are sent (in days)

#### Approval Workflow Settings
- **Require Manager Comments**: Force managers to provide comments when approving/rejecting
- **Allow Self Approval**: Enable employees to approve their own timesheets (not recommended)
- **Allow Draft Editing**: Control whether employees can edit timesheets in draft state
- **Batch Approval Limit**: Set maximum number of timesheets that can be processed in batch operations

#### Auto-Approval Rules
- **Auto-approve Standard Hours**: Automatically approve timesheets within standard working hours
- **Standard Hours Threshold**: Set the daily hours threshold for auto-approval (0-24 hours)

#### Integration Settings
- **Project Allocation Integration**: Validate timesheet entries against project allocations
- **Customer Portal Access**: Allow customers to view and approve project timesheets via portal

#### Administrative Tools
- **Test Email Settings**: Send test emails to verify notification configuration
- **Reset to Defaults**: Restore all settings to their default values with confirmation

### Dynamic Configuration Application

All configuration settings are applied in real-time throughout the system:
- Email notifications respect individual toggle settings
- Batch operations enforce configured limits with validation
- Approval/rejection processes validate required comments
- Cron job reminders use configured frequency settings

### Legacy Configuration Access

Advanced users can also access configuration parameters directly via:
`Settings` → `Technical` → `Parameters` → `System Parameters`

All settings are stored with the prefix `timesheet_approval.` for easy identification.

### Email Templates

Customize notification templates in `Settings` → `Technical` → `Email Templates`:

- **Submission Confirmation**: Sent to employees upon submission
- **Approval Request**: Sent to managers for pending approvals
- **Approval Confirmation**: Sent when timesheet is approved
- **Rejection Notice**: Sent when timesheet is rejected

### Approval Hierarchy

Configure complex approval hierarchies:

1. **Department-Based**: Approve based on employee department
2. **Project-Based**: Approve based on project assignments
3. **Matrix Approval**: Multiple approvers for different criteria
4. **Delegation**: Temporary approval delegation during absences

## 📊 Reports and Analytics

### Standard Reports

1. **Timesheet Approval Summary**:
   - Overview of all submissions by status
   - Filter by employee, department, or date range
   - Export to PDF or Excel

2. **Manager Performance Report**:
   - Approval turnaround times by manager
   - Efficiency metrics and trends
   - Workload distribution analysis

3. **Employee Compliance Report**:
   - Submission timeliness by employee
   - Rejection rates and common issues
   - Training needs identification

### Dashboard Widgets

- **Pending Approvals**: Real-time count of submissions awaiting approval
- **Approval Trends**: Visual charts showing approval patterns
- **Efficiency Metrics**: Average approval times and processing volumes
- **Compliance Indicators**: Submission rates and deadline adherence

## 🔌 API Reference

### REST Endpoints

The module provides RESTful API endpoints for external integrations:

```python
# Get pending approvals
GET /api/timesheet-approval/pending

# Submit timesheet for approval
POST /api/timesheet-approval/submit
{
    "employee_id": 1,
    "date_from": "2024-01-01",
    "date_to": "2024-01-07"
}

# Approve/Reject submission
PUT /api/timesheet-approval/{id}/action
{
    "action": "approve",  # or "reject"
    "comments": "Approval comments"
}
```

### Python API

```python
# Create approval submission
approval = env['timesheet.approval'].create({
    'employee_id': employee.id,
    'date_from': date_from,
    'date_to': date_to,
})

# Submit for approval
approval.action_submit()

# Approve submission
approval.action_approve(comments="Approved after review")

# Reject submission
approval.action_reject(comments="Please correct time entries")
```

## 🔍 Troubleshooting

### Common Issues

1. **Email Notifications Not Sending**:
   - Check outgoing mail server configuration
   - Verify email templates are active
   - Ensure users have valid email addresses

2. **Permissions Issues**:
   - Verify user groups are correctly assigned
   - Check record rules and access rights
   - Review manager assignment in employee records

3. **Performance Issues**:
   - Monitor database query performance
   - Consider indexing for large datasets
   - Review batch operation sizes

### Debug Mode

Enable debug mode for detailed error information:
- Add `?debug=1` to URL
- Check server logs for detailed error messages
- Use browser developer tools for client-side issues

### Log Analysis

Monitor Odoo logs for module-specific issues:
```bash
tail -f /var/log/odoo/odoo.log | grep timesheet_approval
```

## 🤝 Support and Contributing

### Getting Help

- **Documentation**: Comprehensive inline help and tooltips
- **Community Forum**: Post questions in Odoo Community forums
- **GitHub Issues**: Report bugs and feature requests

### Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request with detailed description

### Development Setup

```bash
# Clone development repository
git clone <dev-repo-url>
cd timesheet_approval

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

## 📄 License

This module is licensed under LGPL-3.0. See [LICENSE](LICENSE) file for details.

## 🏢 Credits

**Developed by**: OneTo7 Services  
**Website**: https://www.oneto7.com  
**Version**: 18.0.1.0.0  
**Compatibility**: Odoo 18.0 Community Edition

---

## 📋 Changelog

### Version 18.0.1.0.0 (Latest)
- Initial release for Odoo 18
- Complete workflow implementation
- Mobile-responsive design
- Advanced reporting capabilities
- API endpoints for integrations

### Roadmap
- **v1.1.0**: Advanced approval routing
- **v1.2.0**: Integration with external time tracking tools
- **v1.3.0**: Mobile app companion
- **v2.0.0**: AI-powered approval suggestions

---

*For more information, visit our [website](https://www.oneto7.com) or contact our support team.*

1. **Submit Timesheets**:
   - Navigate to Timesheets → My Timesheets → Submit for Approval
   - Select the period and review timesheet entries
   - Submit for manager approval

2. **Track Status**:
   - View submission status in employee dashboard
   - Receive email notifications for approval/rejection
   - Edit and resubmit if rejected

### For Managers

1. **Review Submissions**:
   - Access pending approvals from manager dashboard
   - Review timesheet details and allocation compliance
   - Add approval comments

2. **Batch Operations**:
   - Use batch approval wizard for multiple submissions
   - Filter and select specific submissions
   - Apply bulk approve/reject actions

3. **Monitoring**:
   - Track approval statistics and team productivity
   - Generate approval reports
   - Monitor compliance and allocation accuracy

### For HR/Admin

1. **Configuration**:
   - Set up approval hierarchies and delegation rules
   - Configure email templates and notification schedules
   - Manage approval policies and requirements

2. **Reporting**:
   - Access comprehensive approval reports
   - Monitor system-wide approval metrics
   - Export data for external analysis

## Technical Details

### Models

- **timesheet.approval**: Main approval object with workflow states
- **timesheet.approval.line**: Individual timesheet entries within approval
- **timesheet.approval.history**: Audit trail for all approval actions
- **hr.employee**: Extended with approval settings and statistics
- **project.project**: Extended with project-level approval configuration

### Security

- **User Groups**:
  - Timesheet Approval User: Submit own timesheets
  - Timesheet Approval Manager: Approve team timesheets
  - Timesheet Approval Admin: Full system access

- **Record Rules**: Ensure users only access appropriate records
- **Access Rights**: Granular permissions for all models and operations

### Workflow States

```
Draft → Submitted → Approved
  ↑         ↓
  ←─── Rejected ──
```

- **Draft**: Employee can edit timesheet entries
- **Submitted**: Awaiting manager approval, locked for editing
- **Approved**: Approved by manager, permanently locked
- **Rejected**: Rejected with comments, returns to draft for revision

## Configuration Options

### Employee Settings
- `requires_timesheet_approval`: Enable approval workflow for employee
- `approval_manager_id`: Designated approval manager
- `can_approve_timesheets`: Allow employee to approve others' timesheets
- `approval_delegation_ids`: Temporary approval delegation settings

### Project Settings
- `requires_timesheet_approval`: Project-specific approval requirement
- `approval_manager_id`: Project-specific approval manager
- `auto_approve_allocated_hours`: Auto-approve if within allocation limits

### System Settings
- Email template customization
- Approval reminder schedules
- Dashboard configuration options

## Customization

### Adding Custom Fields
```python
# Extend approval model
class TimesheetApproval(models.Model):
    _inherit = 'timesheet.approval'
    
    custom_field = fields.Char('Custom Field')
```

### Custom Approval Logic
```python
# Override approval method
def action_approve(self):
    # Custom validation logic
    if self.total_hours > 50:
        raise UserError("Cannot approve more than 50 hours per week")
    return super().action_approve()
```

### Email Template Customization
Modify templates in `data/mail_template_data.xml` to customize notification content and styling.

## Troubleshooting

### Common Issues

1. **Approval Button Not Visible**:
   - Check user permissions and group membership
   - Verify manager assignment for employee
   - Ensure timesheet approval is enabled for employee

2. **Email Notifications Not Sent**:
   - Check email server configuration
   - Verify email templates are active
   - Check scheduled action settings

3. **Performance Issues**:
   - Index database tables for large datasets
   - Configure batch size for bulk operations
   - Optimize approval queries and filters

### Debug Mode
Enable developer mode to access technical features:
- View approval workflow logs
- Check permission assignments
- Monitor email queue status

## Support and Development

### Contributing
1. Fork the repository
2. Create feature branch
3. Follow Odoo development guidelines
4. Submit pull request with tests

### Bug Reports
Please include:
- Odoo version and module version
- Steps to reproduce the issue
- Error messages and logs
- System configuration details

### Feature Requests
Submit enhancement requests with:
- Clear use case description
- Expected behavior
- Integration requirements
- Business justification

## License

This module is licensed under LGPL-3. See LICENSE file for details.

## Credits

Developed by OneTo7 Services for the Odoo Community.

For support and customization services, contact: support@oneto7.com
