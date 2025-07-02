# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class TimesheetSubmissionWizardSimple(models.TransientModel):
    _name = 'timesheet.submission.wizard.simple'
    _description = 'Simple Timesheet Submission Wizard (No History)'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.user.employee_id,
    )
    
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.today() - timedelta(days=7),
    )
    
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=lambda self: fields.Date.today(),
    )
    
    preview_html = fields.Html(
        string='Timesheet Preview',
        compute='_compute_preview',
    )
    
    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_preview(self):
        for record in self:
            if not (record.employee_id and record.date_from and record.date_to):
                record.preview_html = "<p>Please select employee and date range.</p>"
                continue
                
            # Get timesheet entries
            timesheets = self.env['account.analytic.line'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
            ])
            
            if not timesheets:
                record.preview_html = f"""
                <div class="alert alert-warning">
                    <h4>No Timesheet Entries Found</h4>
                    <p>No timesheet entries found for {record.employee_id.name} 
                    from {record.date_from} to {record.date_to}.</p>
                    <p><strong>To resolve this:</strong></p>
                    <ul>
                        <li>Go to Timesheets → My Timesheets</li>
                        <li>Create timesheet entries for the selected period</li>
                        <li>Return here to submit for approval</li>
                    </ul>
                </div>
                """
                continue
            
            # Build HTML preview
            total_hours = sum(ts.unit_amount for ts in timesheets)
            html = f"""
            <div class="alert alert-success">
                <h4>Found {len(timesheets)} timesheet entries ({total_hours:.1f} hours total)</h4>
            </div>
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Project</th>
                        <th>Task</th>
                        <th>Description</th>
                        <th>Hours</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for ts in timesheets.sorted('date'):
                project_name = ts.project_id.name if ts.project_id else 'No Project'
                task_name = ts.task_id.name if ts.task_id else ''
                description = ts.name or 'No description'
                
                html += f"""
                <tr>
                    <td>{ts.date}</td>
                    <td>{project_name}</td>
                    <td>{task_name}</td>
                    <td>{description}</td>
                    <td>{ts.unit_amount:.1f}h</td>
                </tr>
                """
            
            html += f"""
                </tbody>
                <tfoot>
                    <tr class="table-info">
                        <th colspan="4">Total Hours:</th>
                        <th>{total_hours:.1f}h</th>
                    </tr>
                </tfoot>
            </table>
            """
            
            record.preview_html = html
    
    def action_submit_simple(self):
        """Simple submission without history records"""
        self.ensure_one()
        
        if not self.employee_id:
            raise UserError(_("Please select an employee."))
        
        # Get manager
        manager = self.employee_id.parent_id
        if not manager:
            raise UserError(_("No manager assigned to this employee. Please contact HR."))
        
        # Get timesheet entries
        timesheets = self.env['account.analytic.line'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ])
        
        if not timesheets:
            raise UserError(_("No timesheet entries found for the selected period."))
        
        # Create timesheet approval (simplified)
        try:
            approval = self.env['timesheet.approval'].create({
                'employee_id': self.employee_id.id,
                'manager_id': manager.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'state': 'submitted',
                'submission_date': fields.Datetime.now(),
                'submitted_by': self.env.user.id,
            })
            
            # Create approval lines
            for ts in timesheets:
                self.env['timesheet.approval.line'].create({
                    'approval_id': approval.id,
                    'analytic_line_id': ts.id,
                    'date': ts.date,
                    'employee_id': ts.employee_id.id,
                    'project_id': ts.project_id.id if ts.project_id else False,
                    'task_id': ts.task_id.id if ts.task_id else False,
                    'unit_amount': ts.unit_amount,
                    'name': ts.name or 'No description',
                })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success!'),
                    'message': f'Timesheet submitted successfully! '
                              f'Approval ID: {approval.id} with {len(timesheets)} entries.',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(f"Failed to create timesheet approval: {e}")
