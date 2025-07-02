# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Timesheet Approval Settings
    timesheet_approval_required = fields.Boolean(
        string='Timesheet Approval Required',
        default=True,
        help="Whether this employee's timesheets require approval"
    )
    
    timesheet_manager_id = fields.Many2one(
        'hr.employee',
        string='Timesheet Manager',
        compute='_compute_timesheet_manager',
        store=True,
        help="Manager responsible for timesheet approvals (defaults to direct manager)"
    )
    
    # Statistics
    timesheet_approval_ids = fields.One2many(
        'timesheet.approval',
        'employee_id',
        string='Timesheet Approvals',
        help="All timesheet approval records for this employee"
    )
    
    pending_timesheet_count = fields.Integer(
        string='Pending Timesheets',
        compute='_compute_timesheet_counts',
        help="Number of pending timesheet approvals"
    )
    
    approved_timesheet_count = fields.Integer(
        string='Approved Timesheets',
        compute='_compute_timesheet_counts',
        help="Number of approved timesheets this month"
    )
    
    last_timesheet_submission = fields.Datetime(
        string='Last Submission',
        compute='_compute_last_submission',
        help="Date of last timesheet submission"
    )
    
    @api.depends('parent_id')
    def _compute_timesheet_manager(self):
        """Compute timesheet manager (defaults to direct manager)"""
        for employee in self:
            employee.timesheet_manager_id = employee.parent_id or False
    
    @api.depends('timesheet_approval_ids.state')
    def _compute_timesheet_counts(self):
        """Compute timesheet approval counts"""
        for employee in self:
            approvals = employee.timesheet_approval_ids
            employee.pending_timesheet_count = len(approvals.filtered(lambda a: a.state == 'submitted'))
            
            # Approved timesheets this month
            from datetime import datetime, date
            current_month_start = date.today().replace(day=1)
            employee.approved_timesheet_count = len(approvals.filtered(
                lambda a: a.state == 'approved' and 
                a.approval_date and 
                a.approval_date.date() >= current_month_start
            ))
    
    @api.depends('timesheet_approval_ids.submission_date')
    def _compute_last_submission(self):
        """Compute last timesheet submission date"""
        for employee in self:
            submitted_approvals = employee.timesheet_approval_ids.filtered(
                lambda a: a.submission_date
            ).sorted('submission_date', reverse=True)
            
            employee.last_timesheet_submission = (
                submitted_approvals[0].submission_date if submitted_approvals else False
            )
    
    def action_view_timesheet_approvals(self):
        """Action to view employee's timesheet approvals"""
        self.ensure_one()
        
        action = self.env.ref('timesheet_approval.action_timesheet_approval_employee').read()[0]
        action['domain'] = [('employee_id', '=', self.id)]
        action['context'] = {
            'default_employee_id': self.id,
            'search_default_employee_id': self.id,
        }
        
        return action
    
    def action_create_timesheet_approval(self):
        """Action to create new timesheet approval"""
        self.ensure_one()
        
        action = self.env.ref('timesheet_approval.action_timesheet_approval_form').read()[0]
        action['context'] = {
            'default_employee_id': self.id,
        }
        action['views'] = [(False, 'form')]
        action['target'] = 'new'
        
        return action
    
    @api.model
    def get_employees_requiring_approval(self):
        """Get employees who need to submit timesheets"""
        return self.search([
            ('timesheet_approval_required', '=', True),
            ('active', '=', True),
        ])
    
    def check_pending_timesheet_submissions(self):
        """Check if employee has pending timesheet submissions"""
        self.ensure_one()
        
        # Look for gaps in timesheet submissions
        from datetime import datetime, timedelta, date
        
        # Check last 30 days for missing submissions
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        # Get all approved/submitted timesheets in this period
        existing_approvals = self.timesheet_approval_ids.filtered(
            lambda a: a.state in ['submitted', 'approved'] and
            a.date_from <= end_date and a.date_to >= start_date
        )
        
        # Simple check - if no timesheet submitted in last 7 days, flag as pending
        recent_submission = self.timesheet_approval_ids.filtered(
            lambda a: a.submission_date and
            a.submission_date.date() >= (end_date - timedelta(days=7))
        )
        
        return not bool(recent_submission)
    
    @api.model
    def _send_timesheet_submission_reminders(self):
        """
        Cron job method to send reminders to employees who haven't submitted timesheets
        """
        # Check if reminder emails are enabled in configuration
        settings = self.env['timesheet.approval.settings']
        reminder_enabled = settings.get_config_value('email_reminder_enabled', True)
        
        if not reminder_enabled:
            return
        
        # Find employees who need to submit timesheets
        employees = self.search([
            ('timesheet_approval_required', '=', True),
            ('active', '=', True)
        ])
        
        reminder_count = 0
        for employee in employees:
            if employee.has_pending_timesheet_submission():
                # Send reminder notification
                employee.message_post(
                    body=f"""
                    <p>Hi {employee.name},</p>
                    <p>This is a friendly reminder that you have pending timesheet submissions.</p>
                    <p>Please submit your timesheets for manager approval at your earliest convenience.</p>
                    <p>Best regards,<br/>HR Department</p>
                    """,
                    subject="Timesheet Submission Reminder",
                    subtype_xmlid='mail.mt_comment'
                )
                reminder_count += 1
        
        if reminder_count > 0:
            self.env['ir.logging'].sudo().create({
                'name': 'timesheet.approval.reminder',
                'type': 'server',
                'level': 'INFO',
                'message': f'Sent timesheet submission reminders to {reminder_count} employees',
            })
        
        return True
