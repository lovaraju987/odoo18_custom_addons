# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date

class TimesheetSubmissionWizard(models.TransientModel):
    _name = 'timesheet.submission.wizard'
    _description = 'Timesheet Submission Wizard'

    @api.model
    def default_get(self, fields_list):
        """Ensure timesheet entries are loaded when wizard opens"""
        res = super().default_get(fields_list)
        
        # Auto-load timesheet entries if dates are available
        if 'date_from' in res and 'date_to' in res and 'employee_id' in res:
            self._load_timesheet_entries_for_defaults(res)
        
        return res
    
    def _load_timesheet_entries_for_defaults(self, vals):
        """Load timesheet entries for default_get"""
        try:
            employee_id = vals.get('employee_id')
            date_from = vals.get('date_from')
            date_to = vals.get('date_to')
            
            if employee_id and date_from and date_to:
                # Find timesheet entries
                timesheet_lines = self.env['account.analytic.line'].search([
                    ('employee_id', '=', employee_id),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                ])
                
                # Create line data
                line_vals = []
                for line in timesheet_lines:
                    line_vals.append((0, 0, {
                        'analytic_line_id': line.id,
                        'date': line.date,
                        'employee_id': line.employee_id.id,
                        'project_id': line.project_id.id if line.project_id else False,
                        'task_id': line.task_id.id if line.task_id else False,
                        'unit_amount': line.unit_amount,
                        'name': line.name or 'No description',
                    }))
                
                vals['timesheet_line_ids'] = line_vals
                vals['total_hours'] = sum(line.unit_amount for line in timesheet_lines)
                vals['total_entries'] = len(timesheet_lines)
                
        except Exception as e:
            # Don't break wizard creation if loading fails
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f"Failed to load timesheet entries in default_get: {e}")

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
    
    # Advanced Options
    include_entries_without_projects = fields.Boolean(
        string='Include Entries Without Projects',
        default=False,
        help="Include timesheet entries that don't have a project assigned (may require admin approval)"
    )

    def action_refresh_entries(self):
        """Manual refresh button for timesheet entries"""
        self._load_timesheet_entries()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
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
    
    @api.onchange('employee_id', 'date_from', 'date_to', 'include_entries_without_projects')
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
        
        # Debug: Check all timesheet entries for this employee in the period
        all_entries = self.env['account.analytic.line'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ])
        
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info(f"Found {len(all_entries)} total timesheet entries for {self.employee_id.name} "
                    f"from {self.date_from} to {self.date_to}")
        
        # Log details of all entries for debugging
        for entry in all_entries:
            _logger.info(f"Entry: ID={entry.id}, Date={entry.date}, Project={entry.project_id.name if entry.project_id else 'NO PROJECT'}, "
                        f"Hours={entry.unit_amount}, Desc='{entry.name[:50] if entry.name else ''}...'")
        
        # Determine which entries to include
        if self.include_entries_without_projects:
            # Include all timesheet entries
            timesheet_entries = all_entries
            _logger.info(f"Including all {len(timesheet_entries)} timesheet entries (with and without projects)")
        else:
            # Find timesheet entries with projects only
            timesheet_entries = all_entries.filtered(lambda line: line.project_id)
            _logger.info(f"Found {len(timesheet_entries)} timesheet entries with project assignments")
        
        # If no entries found, provide helpful information
        if not timesheet_entries:
            entries_without_projects = all_entries.filtered(lambda line: not line.project_id)
            if entries_without_projects and not self.include_entries_without_projects:
                _logger.warning(f"Found {len(entries_without_projects)} timesheet entries without project assignments. "
                              f"User may need to enable 'Include Entries Without Projects' option.")
            elif not all_entries:
                _logger.warning(f"No timesheet entries found for {self.employee_id.name} "
                              f"from {self.date_from} to {self.date_to}")
        
        # Create wizard lines
        wizard_lines = []
        for entry in timesheet_entries:
            line_data = {
                'analytic_line_id': entry.id,
                'date': entry.date,
                'unit_amount': entry.unit_amount,
                'name': entry.name or 'No description provided',
            }
            
            # Only set project_id if entry has a project
            if entry.project_id:
                line_data['project_id'] = entry.project_id.id
                line_data['task_id'] = entry.task_id.id if entry.task_id else False
            
            wizard_lines.append((0, 0, line_data))
        
        self.timesheet_line_ids = wizard_lines
    
    def action_submit_timesheet(self):
        """Create and submit timesheet approval"""
        self.ensure_one()
        
        if not self.timesheet_line_ids:
            # Check if there are any timesheet entries at all for better error message
            all_entries = self.env['account.analytic.line'].search([
                ('employee_id', '=', self.employee_id.id),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
            ])
            
            if not all_entries:
                raise UserError(_(
                    "No timesheet entries found for %s from %s to %s. "
                    "Please create timesheet entries first in Timesheets > My Timesheets."
                ) % (self.employee_id.name, self.date_from, self.date_to))
            else:
                # There are entries but none were loaded
                entries_without_projects = all_entries.filtered(lambda line: not line.project_id)
                if entries_without_projects and not self.include_entries_without_projects:
                    raise UserError(_(
                        "Found %d timesheet entries for the selected period, but %d entries "
                        "do not have projects assigned. \n\n"
                        "Option 1: Assign projects to your timesheet entries in Timesheets > My Timesheets.\n"
                        "Option 2: Enable 'Include Entries Without Projects' option below and resubmit."
                    ) % (len(all_entries), len(entries_without_projects)))
                else:
                    raise UserError(_("No timesheet entries found for the selected period. "
                                    "Please check your timesheet entries and try again."))
        
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

    @api.model
    def default_get(self, fields_list):
        """Set default values and load timesheet entries"""
        res = super().default_get(fields_list)
        
        # If we have an employee context, set it
        if self.env.context.get('default_employee_id'):
            res['employee_id'] = self.env.context['default_employee_id']
        elif not res.get('employee_id'):
            # Get current user's employee record
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            if employee:
                res['employee_id'] = employee.id
        
        return res

    @api.model
    def create(self, vals):
        """Override create to load timesheet entries after creation"""
        wizard = super().create(vals)
        
        # Load timesheet entries after creation if we have the required fields
        if wizard.employee_id and wizard.date_from and wizard.date_to:
            wizard._load_timesheet_entries()
        
        return wizard


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
        required=False,  # Made optional to support entries without projects
        help="Project (if assigned)"
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
