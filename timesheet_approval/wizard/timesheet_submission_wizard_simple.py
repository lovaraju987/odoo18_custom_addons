# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TimesheetSubmissionWizardSimple(models.TransientModel):
    _name = 'timesheet.submission.wizard.simple'
    _description = 'Simple Timesheet Submission Wizard'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.user.employee_id,
    )
    
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=fields.Date.today().replace(day=1),
    )
    
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today(),
    )
    
    def action_submit_timesheet_simple(self):
        """Simple timesheet submission"""
        self.ensure_one()
        
        # Find timesheet entries
        entries = self.env['account.analytic.line'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ])
        
        if not entries:
            raise UserError(_("No timesheet entries found for the selected period."))
        
        # Check manager
        if not self.employee_id.parent_id:
            raise UserError(_("No manager assigned to this employee."))
        
        # Create approval record
        approval = self.env['timesheet.approval'].create({
            'employee_id': self.employee_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'manager_id': self.employee_id.parent_id.id,
        })
        
        # Create approval lines directly
        approval_lines = []
        for entry in entries:
            line_data = {
                'approval_id': approval.id,
                'analytic_line_id': entry.id,
                'date': entry.date,
                'employee_id': entry.employee_id.id,
                'unit_amount': entry.unit_amount,
                'name': entry.name or 'No description',
            }
            
            if entry.project_id:
                line_data['project_id'] = entry.project_id.id
                line_data['task_id'] = entry.task_id.id if entry.task_id else False
            
            approval_lines.append(line_data)
        
        if approval_lines:
            self.env['timesheet.approval.line'].create(approval_lines)
        
        # Set to submitted state
        approval.write({
            'state': 'submitted',
            'submission_date': fields.Datetime.now(),
            'submitted_by': self.env.user.id,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Timesheet Submitted'),
            'res_model': 'timesheet.approval',
            'res_id': approval.id,
            'view_mode': 'form',
            'target': 'current',
        }
