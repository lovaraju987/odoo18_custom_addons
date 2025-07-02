# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date

class TimesheetSubmissionWizard(models.TransientModel):
    _name = 'timesheet.submission.wizard'
    _description = 'Timesheet Submission Wizard'

    # Employee Selection
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.user.employee_id,
        help="Employee for timesheet submission"
    )
    
    # Date Range Selection
    period_type = fields.Selection([
        ('week', 'Weekly'),
        ('month', 'Monthly'),
        ('custom', 'Custom Period'),
    ], string='Period Type', default='week', required=True,
       help="Type of period for timesheet submission")
    
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: self._default_date_from(),
        help="Start date of timesheet period"
    )
    
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=lambda self: self._default_date_to(),
        help="End date of timesheet period"
    )
    
    # Timesheet Information
    timesheet_line_ids = fields.One2many(
        'timesheet.submission.line',
        'wizard_id',
        string='Timesheet Lines',
        help="Timesheet entries for the period"
    )
    
    # Summary
    total_hours = fields.Float(
        string='Total Hours',
        compute='_compute_summary',
        help="Total hours for the period"
    )
    
    total_days = fields.Integer(
        string='Working Days',
        compute='_compute_summary',
        help="Number of working days with entries"
    )
    
    # Validation
    has_existing_submission = fields.Boolean(
        string='Has Existing Submission',
        compute='_compute_validation',
        help="Whether there's already a submission for this period"
    )
    
    validation_messages = fields.Text(
        string='Validation Messages',
        compute='_compute_validation',
        help="Validation messages and warnings"
    )
    
    def _default_date_from(self):
        """Default start date (beginning of current week)"""
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        return monday
    
    def _default_date_to(self):
        """Default end date (end of current week)"""
        today = date.today()
        sunday = today + timedelta(days=(6 - today.weekday()))
        return sunday
    
    @api.depends('timesheet_line_ids.unit_amount')
    def _compute_summary(self):
        """Compute summary information"""
        for wizard in self:
            lines = wizard.timesheet_line_ids
            wizard.total_hours = sum(lines.mapped('unit_amount'))
            wizard.total_days = len(set(lines.mapped('date')))
    
    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_validation(self):
        """Compute validation status"""
        for wizard in self:
            messages = []
            
            # Check for existing submissions
            if wizard.employee_id and wizard.date_from and wizard.date_to:
                existing = self.env['timesheet.approval'].search([
                    ('employee_id', '=', wizard.employee_id.id),
                    ('date_from', '<=', wizard.date_to),
                    ('date_to', '>=', wizard.date_from),
                    ('state', 'in', ['submitted', 'approved']),
                ])
                
                wizard.has_existing_submission = bool(existing)
                
                if existing:
                    messages.append(
                        f"Warning: Overlapping timesheet submission exists for period "
                        f"{existing[0].date_from} to {existing[0].date_to} "
                        f"(Status: {existing[0].state})"
                    )
            else:
                wizard.has_existing_submission = False
            
            wizard.validation_messages = '\n'.join(messages) if messages else False
    
    @api.onchange('period_type')
    def _onchange_period_type(self):
        """Update date range based on period type"""
        today = date.today()
        
        if self.period_type == 'week':
            # Current week (Monday to Sunday)
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            self.date_from = monday
            self.date_to = sunday
            
        elif self.period_type == 'month':
            # Current month
            self.date_from = today.replace(day=1)
            # Last day of month
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month = today.replace(month=today.month + 1, day=1)
            self.date_to = next_month - timedelta(days=1)
    
    @api.onchange('employee_id', 'date_from', 'date_to')
    def _onchange_period(self):
        """Load timesheet entries when period changes"""
        if self.employee_id and self.date_from and self.date_to:
            self._load_timesheet_entries()
    
    def _load_timesheet_entries(self):
        """Load existing timesheet entries for the period"""
        # Clear existing lines
        self.timesheet_line_ids = [(5, 0, 0)]
        
        if not (self.employee_id and self.date_from and self.date_to):
            return
        
        # Find timesheet entries
        timesheet_entries = self.env['account.analytic.line'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('project_id', '!=', False),  # Only project timesheets
        ])
        
        # Create wizard lines
        wizard_lines = []
        for entry in timesheet_entries:
            wizard_lines.append((0, 0, {
                'analytic_line_id': entry.id,
                'date': entry.date,
                'project_id': entry.project_id.id,
                'task_id': entry.task_id.id if entry.task_id else False,
                'unit_amount': entry.unit_amount,
                'name': entry.name,
            }))
        
        self.timesheet_line_ids = wizard_lines
    
    def action_submit_timesheet(self):
        """Create and submit timesheet approval"""
        self.ensure_one()
        
        if not self.timesheet_line_ids:
            raise UserError(_("No timesheet entries found for the selected period."))
        
        if self.has_existing_submission:
            raise UserError(_(
                "There is already a timesheet submission for this period. "
                "Please select a different date range."
            ))
        
        # Create timesheet approval
        approval = self.env['timesheet.approval'].create({
            'employee_id': self.employee_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        # Submit the timesheet
        approval.action_submit()
        
        # Return action to view the created approval
        return {
            'type': 'ir.actions.act_window',
            'name': _('Timesheet Submitted'),
            'res_model': 'timesheet.approval',
            'res_id': approval.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_preview_timesheet(self):
        """Preview timesheet before submission"""
        self.ensure_one()
        
        if not self.timesheet_line_ids:
            raise UserError(_("No timesheet entries found for the selected period."))
        
        # Create temporary approval for preview
        approval = self.env['timesheet.approval'].create({
            'employee_id': self.employee_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        # Load timesheet lines
        approval._load_timesheet_lines()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Timesheet Preview'),
            'res_model': 'timesheet.approval',
            'res_id': approval.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'preview_mode': True},
        }


class TimesheetSubmissionLine(models.TransientModel):
    _name = 'timesheet.submission.line'
    _description = 'Timesheet Submission Line'

    wizard_id = fields.Many2one(
        'timesheet.submission.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    
    analytic_line_id = fields.Many2one(
        'account.analytic.line',
        string='Timesheet Entry',
        help="Original timesheet entry"
    )
    
    date = fields.Date(
        string='Date',
        required=True
    )
    
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True
    )
    
    task_id = fields.Many2one(
        'project.task',
        string='Task'
    )
    
    unit_amount = fields.Float(
        string='Hours',
        required=True
    )
    
    name = fields.Text(
        string='Description',
        required=True
    )
