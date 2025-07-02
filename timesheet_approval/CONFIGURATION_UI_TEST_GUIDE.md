# Configuration UI Test Guide

## Testing the Timesheet Approval Configuration UI

### Prerequisites
1. Install the timesheet_approval module in your Odoo 18 instance
2. Ensure you have manager/admin privileges

### Test Steps

#### 1. Access Configuration
- Navigate to: **Timesheets > Timesheet Approvals > Configuration > Settings**
- Verify the configuration form loads without errors

#### 2. Test Configuration Fields
- **Deadline Settings**: Modify submission and approval deadline days
- **Email Notifications**: Toggle email notification settings
- **Approval Workflow**: Test workflow configuration options
- **Auto-Approval**: Configure auto-approval rules
- **Integration Settings**: Enable/disable integration features

#### 3. Test Buttons
- **Test Email Settings**: Verify test email functionality
- **Reset to Defaults**: Test reset functionality (with confirmation)

#### 4. Test Configuration Integration
- Submit a timesheet and verify email notifications respect configuration
- Try batch approval and ensure batch limits are enforced
- Test approval/rejection with required comments setting

#### 5. Test Persistence
- Save configuration changes
- Logout and login again
- Verify settings are preserved

### Expected Behavior
- All configuration fields should save and load properly
- Email settings should control actual email sending
- Batch limits should be enforced in batch operations
- Required comments setting should be enforced in approval/rejection

### Configuration Parameters
The following parameters are stored in `ir.config_parameter`:
- `timesheet_approval.submission_deadline_days`
- `timesheet_approval.approval_deadline_days`
- `timesheet_approval.email_submission_enabled`
- `timesheet_approval.email_approval_enabled`
- `timesheet_approval.email_reminder_enabled`
- `timesheet_approval.require_manager_comments`
- `timesheet_approval.batch_approval_limit`
- And more...

### Troubleshooting
If you encounter issues:
1. Check Odoo logs for any errors
2. Verify all files are properly loaded
3. Ensure database is updated after module installation
4. Check user permissions (Settings access requires manager group)

### Integration Points
The configuration settings integrate with:
- Email notification methods in `timesheet_approval.py`
- Batch approval wizard in `timesheet_batch_approval.py`
- Cron job reminder methods in `hr_employee.py` and `timesheet_approval.py`
- Approval workflow validation methods
