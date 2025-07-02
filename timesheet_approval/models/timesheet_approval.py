# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class TimesheetApproval(models.Model):
    _name = 'timesheet.approval'
    _description = 'Timesheet Approval'
    _order = 'submission_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'display_name'

    # Basic Information
    display_name = fields.Char(
        string='Name',
        compute='_compute_display_name',
        store=True,
        help="Display name for the timesheet approval"
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.user.employee_id,
        help="Employee submitting the timesheet"
    )
    
    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        compute='_compute_manager_id',
        store=True,
        help="Manager responsible for approval"
    )
    
    # Date Range
    date_from = fields.Date(
        string='From Date',
        required=True,
        help="Start date of the timesheet period"
    )
    
    date_to = fields.Date(
        string='To Date', 
        required=True,
        help="End date of the timesheet period"
    )
    
    # Workflow State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True,
       help="Current approval status of the timesheet")
    
    # Submission Information
    submission_date = fields.Datetime(
        string='Submission Date',
        readonly=True,
        help="Date and time when timesheet was submitted"
    )
    
    submitted_by = fields.Many2one(
        'res.users',
        string='Submitted By',
        readonly=True,
        help="User who submitted the timesheet"
    )
    
    # Approval Information
    approval_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        help="Date and time when timesheet was approved/rejected"
    )
    
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        help="User who approved/rejected the timesheet"
    )
    
    approval_comments = fields.Text(
        string='Approval Comments',
        help="Comments from the approver"
    )
    
    # Timesheet Lines
    timesheet_line_ids = fields.One2many(
        'timesheet.approval.line',
        'approval_id',
        string='Timesheet Lines',
        help="Individual timesheet entries"
    )
    
    # Summary Information
    total_hours = fields.Float(
        string='Total Hours',
        compute='_compute_summary',
        store=True,
        help="Total hours in this timesheet period"
    )
    
    total_days = fields.Integer(
        string='Total Days',
        compute='_compute_summary',
        store=True,
        help="Number of working days in this period"
    )
    
    project_count = fields.Integer(
        string='Projects Count',
        compute='_compute_summary',
        store=True,
        help="Number of different projects worked on"
    )
    
    # History and Tracking
    approval_history_ids = fields.One2many(
        'timesheet.approval.history',
        'approval_id',
        string='Approval History',
        help="Complete history of approval actions"
    )
    
    # Portal Access
    access_token = fields.Char(
        string='Access Token',
        copy=False,
        help="Token for portal access"
    )
    
    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_display_name(self):
        """Compute display name for timesheet approval"""
        for record in self:
            if record.employee_id and record.date_from and record.date_to:
                record.display_name = f"{record.employee_id.name} - {record.date_from} to {record.date_to}"
            else:
                record.display_name = f"Timesheet Approval {record.id or 'New'}"
    
    @api.depends('employee_id')
    def _compute_manager_id(self):
        """Compute manager from employee's parent"""
        for record in self:
            if record.employee_id and record.employee_id.parent_id:
                record.manager_id = record.employee_id.parent_id
            else:
                record.manager_id = False
    
    @api.depends('timesheet_line_ids.unit_amount')
    def _compute_summary(self):
        """Compute summary information"""
        for record in self:
            lines = record.timesheet_line_ids
            record.total_hours = sum(lines.mapped('unit_amount'))
            record.total_days = len(set(lines.mapped('date')))
            record.project_count = len(set(lines.mapped('project_id')))
    
    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        """Validate date range"""
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from > record.date_to:
                    raise ValidationError(_("End date must be after start date."))
                
                # Check for overlapping periods for same employee
                overlapping = self.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('id', '!=', record.id),
                    ('state', 'in', ['submitted', 'approved']),
                    '|', '|',
                    '&', ('date_from', '<=', record.date_from), ('date_to', '>=', record.date_from),
                    '&', ('date_from', '<=', record.date_to), ('date_to', '>=', record.date_to),
                    '&', ('date_from', '>=', record.date_from), ('date_to', '<=', record.date_to),
                ])
                
                if overlapping:
                    raise ValidationError(_(
                        "There is already a submitted/approved timesheet for this employee "
                        "that overlaps with the selected period."
                    ))
    
    def action_submit(self):
        """Submit timesheet for approval"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_("Only draft timesheets can be submitted."))
        
        if not self.timesheet_line_ids:
            raise UserError(_("Cannot submit empty timesheet. Please add timesheet entries."))
        
        if not self.manager_id:
            raise UserError(_("No manager assigned to this employee. Please contact HR."))
        
        # Load timesheet lines from actual timesheets
        self._load_timesheet_lines()
        
        # Validate all timesheet lines
        self._validate_timesheet_lines()
        
        self.write({
            'state': 'submitted',
            'submission_date': fields.Datetime.now(),
            'submitted_by': self.env.user.id,
        })
        
        # Create history record
        self._create_history_record('submitted', 'Timesheet submitted for approval')
        
        # Send notification to manager
        self._send_notification_email('submit')
        
        # Post message to chatter
        self.message_post(
            body=_("Timesheet submitted for approval."),
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        return True
    
    def action_approve(self):
        """Approve timesheet"""
        self.ensure_one()
        
        if self.state != 'submitted':
            raise UserError(_("Only submitted timesheets can be approved."))
        
        # Check if current user can approve
        if not self._can_approve():
            raise UserError(_("You don't have permission to approve this timesheet."))
        
        # Check configuration for required comments
        settings = self.env['timesheet.approval.settings']
        require_comments = settings.get_config_value('require_manager_comments', False)
        
        if require_comments and not self.approval_comments:
            raise UserError(_("Manager comments are required for approval. Please provide comments."))
        
        self.write({
            'state': 'approved',
            'approval_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
        })
        
        # Create history record
        self._create_history_record('approved', f'Timesheet approved. {self.approval_comments or ""}')
        
        # Send notification to employee
        self._send_notification_email('approve')
        
        # Post message to chatter
        self.message_post(
            body=_("Timesheet approved."),
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        return True
    
    def action_reject(self):
        """Reject timesheet"""
        self.ensure_one()
        
        if self.state != 'submitted':
            raise UserError(_("Only submitted timesheets can be rejected."))
        
        # Check if current user can approve
        if not self._can_approve():
            raise UserError(_("You don't have permission to reject this timesheet."))
        
        # Check configuration for required comments
        settings = self.env['timesheet.approval.settings']
        require_comments = settings.get_config_value('require_manager_comments', False)
        
        if require_comments and not self.approval_comments:
            raise UserError(_("Manager comments are required for rejection. Please provide rejection comments."))
        
        if not self.approval_comments:
            raise UserError(_("Please provide rejection comments."))
        
        self.write({
            'state': 'rejected',
            'approval_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
        })
        
        # Create history record
        self._create_history_record('rejected', f'Timesheet rejected. {self.approval_comments}')
        
        # Send notification to employee
        self._send_notification_email('reject')
        
        # Post message to chatter
        self.message_post(
            body=_("Timesheet rejected: %s") % self.approval_comments,
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        return True
    
    def action_reset_to_draft(self):
        """Reset timesheet to draft state"""
        self.ensure_one()
        
        if self.state not in ['rejected']:
            raise UserError(_("Only rejected timesheets can be reset to draft."))
        
        self.write({
            'state': 'draft',
            'approval_date': False,
            'approved_by': False,
            'approval_comments': False,
        })
        
        # Create history record
        self._create_history_record('draft', 'Timesheet reset to draft for corrections')
        
        return True
    
    def _can_approve(self):
        """Check if current user can approve this timesheet"""
        user = self.env.user
        
        # System admin can always approve
        if user.has_group('base.group_system'):
            return True
        
        # HR managers can approve
        if user.has_group('hr.group_hr_manager'):
            return True
        
        # Manager can approve their team's timesheets
        if self.manager_id and self.manager_id.user_id == user:
            return True
        
        # Project managers can approve timesheets for their projects
        if user.has_group('project.group_project_manager'):
            project_ids = self.timesheet_line_ids.mapped('project_id')
            managed_projects = self.env['project.project'].search([
                ('user_id', '=', user.id),
                ('id', 'in', project_ids.ids)
            ])
            if managed_projects:
                return True
        
        return False
    
    def _load_timesheet_lines(self):
        """Load actual timesheet entries for the period"""
        # Clear existing lines
        self.timesheet_line_ids.unlink()
        
        # Find timesheet entries in the period
        timesheet_lines = self.env['account.analytic.line'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('project_id', '!=', False),  # Only project-related entries
        ])
        
        # Create approval lines
        approval_lines = []
        for line in timesheet_lines:
            approval_lines.append({
                'approval_id': self.id,
                'analytic_line_id': line.id,
                'date': line.date,
                'project_id': line.project_id.id,
                'task_id': line.task_id.id if line.task_id else False,
                'employee_id': line.employee_id.id,
                'unit_amount': line.unit_amount,
                'name': line.name,
            })
        
        if approval_lines:
            self.env['timesheet.approval.line'].create(approval_lines)
    
    def _validate_timesheet_lines(self):
        """Validate all timesheet lines before submission"""
        for line in self.timesheet_line_ids:
            line._validate_line()
    
    def _create_history_record(self, action, comments=''):
        """Create approval history record"""
        self.env['timesheet.approval.history'].create({
            'approval_id': self.id,
            'action': action,
            'action_date': fields.Datetime.now(),
            'user_id': self.env.user.id,
            'comments': comments,
        })
    
    def _send_notification_email(self, action):
        """Send email notifications based on configuration settings"""
        settings = self.env['timesheet.approval.settings']
        
        # Check if email notifications are enabled for this action
        email_enabled = False
        if action == 'submit':
            email_enabled = settings.get_config_value('email_submission_enabled', True)
        elif action == 'approve':
            email_enabled = settings.get_config_value('email_approval_enabled', True)
        elif action == 'reject':
            email_enabled = settings.get_config_value('email_approval_enabled', True)
        elif action == 'reminder':
            email_enabled = settings.get_config_value('email_reminder_enabled', True)
        
        if not email_enabled:
            _logger.info(f"Email notification for '{action}' is disabled in configuration")
            return
        
        template_ref = f'timesheet_approval.email_template_timesheet_{action}'
        
        try:
            template = self.env.ref(template_ref)
            if template:
                template.send_mail(self.id, force_send=True)
        except Exception as e:
            _logger.warning(f"Failed to send email notification: {e}")
    
    @api.model
    def create_timesheet_approval(self, employee_id, date_from, date_to):
        """Helper method to create timesheet approval"""
        return self.create({
            'employee_id': employee_id,
            'date_from': date_from,
            'date_to': date_to,
        })
    
    def get_portal_url(self):
        """Get portal URL for timesheet approval"""
        return f'/my/timesheet/{self.id}?access_token={self.access_token}'
    
    @api.model
    def _generate_access_token(self):
        """Generate access token for portal access"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def action_view_timesheet_lines(self):
        """Action to view timesheet lines related to this approval"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Timesheet Lines',
            'res_model': 'timesheet.approval.line',
            'view_mode': 'tree,form',
            'domain': [('approval_id', '=', self.id)],
            'context': {'default_approval_id': self.id},
            'target': 'current',
        }

    def action_view_projects(self):
        """Action to view projects related to this approval"""
        project_ids = self.timesheet_line_ids.mapped('project_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Projects',
            'res_model': 'project.project',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', project_ids)],
            'target': 'current',
        }

    @api.model
    def create(self, vals):
        """Override create to generate access token"""
        if not vals.get('access_token'):
            vals['access_token'] = self._generate_access_token()
        return super().create(vals)
    
    @api.model
    def _send_approval_reminders(self):
        """
        Cron job method to send reminders to managers about pending approvals
        """
        # Check if reminder emails are enabled in configuration
        settings = self.env['timesheet.approval.settings']
        reminder_enabled = settings.get_config_value('email_reminder_enabled', True)
        
        if not reminder_enabled:
            return True
        
        # Get reminder frequency from configuration
        reminder_frequency = settings.get_config_value('reminder_frequency_days', 2)
        
        # Find pending approvals older than configured frequency
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=reminder_frequency)
        pending_approvals = self.search([
            ('state', '=', 'submitted'),
            ('submission_date', '<', cutoff_date)
        ])
        
        # Group by manager
        manager_approvals = {}
        for approval in pending_approvals:
            manager = approval.manager_id
            if manager not in manager_approvals:
                manager_approvals[manager] = []
            manager_approvals[manager].append(approval)
        
        reminder_count = 0
        for manager, approvals in manager_approvals.items():
            if manager and manager.user_id:
                # Send reminder notification
                approval_list = "\n".join([
                    f"• {approval.employee_id.name} ({approval.date_from} to {approval.date_to})"
                    for approval in approvals
                ])
                
                manager.message_post(
                    body=f"""
                    <p>Hi {manager.name},</p>
                    <p>You have {len(approvals)} pending timesheet approvals that require your attention:</p>
                    <p>{approval_list}</p>
                    <p>Please review and approve these timesheets at your earliest convenience.</p>
                    <p>Best regards,<br/>HR Department</p>
                    """,
                    subject=f"Pending Timesheet Approvals ({len(approvals)})",
                    subtype_xmlid='mail.mt_comment'
                )
                reminder_count += len(approvals)
        
        if reminder_count > 0:
            self.env['ir.logging'].sudo().create({
                'name': 'timesheet.approval.reminder',
                'type': 'server', 
                'level': 'INFO',
                'message': f'Sent approval reminders for {reminder_count} pending timesheets',
            })
        
        return True
