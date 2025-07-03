# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TimesheetApprovalSettings(models.TransientModel):
    _name = 'timesheet.approval.settings'
    _description = 'Timesheet Approval Settings'
    _inherit = 'res.config.settings'

    # Deadline Settings
    submission_deadline_days = fields.Integer(
        string='Submission Deadline (Days)',
        default=7,
        help="Number of days employees have to submit timesheets after period end"
    )
    
    approval_deadline_days = fields.Integer(
        string='Approval Deadline (Days)', 
        default=3,
        help="Number of days managers have to approve submitted timesheets"
    )
    
    auto_submission_enabled = fields.Boolean(
        string='Enable Auto-Submission',
        default=False,
        help="Automatically submit timesheets when deadline approaches"
    )
    
    # Email Notification Settings
    email_submission_enabled = fields.Boolean(
        string='Submission Notifications',
        default=True,
        help="Send email notifications when timesheets are submitted"
    )
    
    email_approval_enabled = fields.Boolean(
        string='Approval Notifications',
        default=True,
        help="Send email notifications when timesheets are approved/rejected"
    )
    
    email_reminder_enabled = fields.Boolean(
        string='Reminder Notifications',
        default=True,
        help="Send reminder emails for pending submissions and approvals"
    )
    
    reminder_frequency_days = fields.Integer(
        string='Reminder Frequency (Days)',
        default=2,
        help="How often to send reminder emails"
    )
    
    # Approval Settings
    require_manager_comments = fields.Boolean(
        string='Require Manager Comments',
        default=False,
        help="Require managers to add comments when approving/rejecting"
    )
    
    allow_self_approval = fields.Boolean(
        string='Allow Self Approval',
        default=False,
        help="Allow employees to approve their own timesheets (not recommended)"
    )
    
    batch_approval_limit = fields.Integer(
        string='Batch Approval Limit',
        default=50,
        help="Maximum number of timesheets that can be processed in batch"
    )
    
    # Integration Settings
    project_allocation_integration = fields.Boolean(
        string='Project Allocation Integration',
        default=True,
        help="Validate timesheet entries against project allocations"
    )
    
    portal_access_enabled = fields.Boolean(
        string='Customer Portal Access',
        default=False,
        help="Allow customers to view and approve project timesheets via portal"
    )
    
    # Workflow Settings
    allow_draft_editing = fields.Boolean(
        string='Allow Draft Editing',
        default=True,
        help="Allow employees to edit timesheets in draft state"
    )
    
    auto_approve_standard_hours = fields.Boolean(
        string='Auto-approve Standard Hours',
        default=False,
        help="Automatically approve timesheets within standard working hours"
    )
    
    standard_hours_threshold = fields.Float(
        string='Standard Hours Threshold',
        default=8.0,
        help="Daily hours threshold for auto-approval"
    )

    @api.constrains('submission_deadline_days', 'approval_deadline_days', 'reminder_frequency_days', 'batch_approval_limit')
    def _check_positive_values(self):
        """Ensure all numeric settings are positive"""
        for record in self:
            if record.submission_deadline_days <= 0:
                raise ValidationError(_("Submission deadline must be greater than 0 days"))
            if record.approval_deadline_days <= 0:
                raise ValidationError(_("Approval deadline must be greater than 0 days"))
            if record.reminder_frequency_days <= 0:
                raise ValidationError(_("Reminder frequency must be greater than 0 days"))
            if record.batch_approval_limit <= 0:
                raise ValidationError(_("Batch approval limit must be greater than 0"))

    @api.constrains('standard_hours_threshold')
    def _check_hours_threshold(self):
        """Validate hours threshold"""
        for record in self:
            if record.standard_hours_threshold <= 0 or record.standard_hours_threshold > 24:
                raise ValidationError(_("Standard hours threshold must be between 0 and 24 hours"))

    def set_values(self):
        """Save configuration values"""
        super().set_values()
        params = self.env['ir.config_parameter'].sudo()
        
        params.set_param('timesheet_approval.submission_deadline_days', self.submission_deadline_days)
        params.set_param('timesheet_approval.approval_deadline_days', self.approval_deadline_days)
        params.set_param('timesheet_approval.auto_submission_enabled', self.auto_submission_enabled)
        params.set_param('timesheet_approval.email_submission_enabled', self.email_submission_enabled)
        params.set_param('timesheet_approval.email_approval_enabled', self.email_approval_enabled)
        params.set_param('timesheet_approval.email_reminder_enabled', self.email_reminder_enabled)
        params.set_param('timesheet_approval.reminder_frequency_days', self.reminder_frequency_days)
        params.set_param('timesheet_approval.require_manager_comments', self.require_manager_comments)
        params.set_param('timesheet_approval.allow_self_approval', self.allow_self_approval)
        params.set_param('timesheet_approval.batch_approval_limit', self.batch_approval_limit)
        params.set_param('timesheet_approval.project_allocation_integration', self.project_allocation_integration)
        params.set_param('timesheet_approval.portal_access_enabled', self.portal_access_enabled)
        params.set_param('timesheet_approval.allow_draft_editing', self.allow_draft_editing)
        params.set_param('timesheet_approval.auto_approve_standard_hours', self.auto_approve_standard_hours)
        params.set_param('timesheet_approval.standard_hours_threshold', self.standard_hours_threshold)

    @api.model
    def get_values(self):
        """Load configuration values"""
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        
        res.update({
            'submission_deadline_days': int(params.get_param('timesheet_approval.submission_deadline_days', 7)),
            'approval_deadline_days': int(params.get_param('timesheet_approval.approval_deadline_days', 3)),
            'auto_submission_enabled': params.get_param('timesheet_approval.auto_submission_enabled', 'False') == 'True',
            'email_submission_enabled': params.get_param('timesheet_approval.email_submission_enabled', 'True') == 'True',
            'email_approval_enabled': params.get_param('timesheet_approval.email_approval_enabled', 'True') == 'True',
            'email_reminder_enabled': params.get_param('timesheet_approval.email_reminder_enabled', 'True') == 'True',
            'reminder_frequency_days': int(params.get_param('timesheet_approval.reminder_frequency_days', 2)),
            'require_manager_comments': params.get_param('timesheet_approval.require_manager_comments', 'False') == 'True',
            'allow_self_approval': params.get_param('timesheet_approval.allow_self_approval', 'False') == 'True',
            'batch_approval_limit': int(params.get_param('timesheet_approval.batch_approval_limit', 50)),
            'project_allocation_integration': params.get_param('timesheet_approval.project_allocation_integration', 'True') == 'True',
            'portal_access_enabled': params.get_param('timesheet_approval.portal_access_enabled', 'False') == 'True',
            'allow_draft_editing': params.get_param('timesheet_approval.allow_draft_editing', 'True') == 'True',
            'auto_approve_standard_hours': params.get_param('timesheet_approval.auto_approve_standard_hours', 'False') == 'True',
            'standard_hours_threshold': float(params.get_param('timesheet_approval.standard_hours_threshold', 8.0)),
        })
        return res

    @api.model
    def get_config_value(self, key, default=None):
        """Helper method to get configuration values from anywhere in the system"""
        params = self.env['ir.config_parameter'].sudo()
        value = params.get_param(f'timesheet_approval.{key}', default)
        
        # Convert string values to proper types
        if value in ('True', 'False'):
            return value == 'True'
        elif key in ['submission_deadline_days', 'approval_deadline_days', 'reminder_frequency_days', 'batch_approval_limit']:
            return int(value) if value else (default or 0)
        elif key in ['standard_hours_threshold']:
            return float(value) if value else (default or 0.0)
        else:
            return value

    def action_reset_to_defaults(self):
        """Reset all settings to default values"""
        self.ensure_one()
        self.write({
            'submission_deadline_days': 7,
            'approval_deadline_days': 3,
            'auto_submission_enabled': False,
            'email_submission_enabled': True,
            'email_approval_enabled': True,
            'email_reminder_enabled': True,
            'reminder_frequency_days': 2,
            'require_manager_comments': False,
            'allow_self_approval': False,
            'batch_approval_limit': 50,
            'project_allocation_integration': True,
            'portal_access_enabled': False,
            'allow_draft_editing': True,
            'auto_approve_standard_hours': False,
            'standard_hours_threshold': 8.0,
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_test_email_settings(self):
        """Test email configuration by sending a test email"""
        self.ensure_one()
        
        # Check if user has an employee record
        if not self.env.user.employee_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Employee Record'),
                    'message': _('Current user must have an employee record to test emails.'),
                    'type': 'warning',
                }
            }
        
        try:
            # Create a temporary test approval
            test_approval = self.env['timesheet.approval'].create({
                'employee_id': self.env.user.employee_id.id,
                'date_from': fields.Date.today(),
                'date_to': fields.Date.today(),
                'state': 'submitted',
            })
            
            # Try to find and send test email template
            template = self.env.ref('timesheet_approval.email_template_timesheet_submit', raise_if_not_found=False)
            if template:
                template.send_mail(test_approval.id, force_send=True)
                message = _('Test email sent successfully to your email address.')
                msg_type = 'success'
            else:
                message = _('Email template not found. Please check email template configuration.')
                msg_type = 'warning'
            
            # Clean up test data
            test_approval.unlink()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Email Test Result'),
                    'message': message,
                    'type': msg_type,
                }
            }
            
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Email Test Failed'),
                    'message': _('Error occurred while testing email: %s') % str(e),
                    'type': 'danger',
                }
            }
