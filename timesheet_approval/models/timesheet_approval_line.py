# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

class TimesheetApprovalLine(models.Model):
    _name = 'timesheet.approval.line'
    _description = 'Timesheet Approval Line'
    _order = 'date desc, id desc'

    # Parent Reference
    approval_id = fields.Many2one(
        'timesheet.approval',
        string='Timesheet Approval',
        required=True,
        ondelete='cascade',
        help="Parent timesheet approval record"
    )
    
    # Original Timesheet Reference
    analytic_line_id = fields.Many2one(
        'account.analytic.line',
        string='Original Timesheet Entry',
        help="Reference to the original timesheet entry"
    )
    
    # Timesheet Information
    date = fields.Date(
        string='Date',
        required=True,
        help="Date of work"
    )
    
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        help="Project worked on"
    )
    
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        help="Specific task worked on"
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        help="Employee who performed the work"
    )
    
    unit_amount = fields.Float(
        string='Hours',
        required=True,
        help="Number of hours worked"
    )
    
    name = fields.Text(
        string='Description',
        required=True,
        help="Description of work performed"
    )
    
    # Additional Information
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='approval_id.company_id',
        store=True
    )
    
    # Validation Status
    validation_status = fields.Selection([
        ('valid', 'Valid'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ], string='Validation Status', default='valid',
       help="Validation status of this timesheet line")
    
    validation_message = fields.Text(
        string='Validation Message',
        help="Validation message or warning"
    )
    
    # Related Fields for Display
    project_manager = fields.Many2one(
        'res.users',
        string='Project Manager',
        related='project_id.user_id',
        store=False,
        help="Manager of the project"
    )
    
    project_type = fields.Selection(
        string='Project Type',
        related='project_id.project_type',
        store=False,
        help="Type of project"
    )
    
    @api.constrains('unit_amount')
    def _check_unit_amount(self):
        """Validate unit amount"""
        for record in self:
            if record.unit_amount <= 0:
                raise ValidationError(_("Hours must be greater than 0."))
            
            if record.unit_amount > 24:
                raise ValidationError(_("Cannot log more than 24 hours in a single day."))
    
    @api.constrains('date', 'approval_id')
    def _check_date_in_period(self):
        """Ensure date is within approval period"""
        for record in self:
            if record.approval_id and record.date:
                if not (record.approval_id.date_from <= record.date <= record.approval_id.date_to):
                    raise ValidationError(_(
                        "Timesheet entry date must be within the approval period "
                        "(%s to %s)."
                    ) % (record.approval_id.date_from, record.approval_id.date_to))
    
    def _validate_line(self):
        """Validate individual timesheet line"""
        self.ensure_one()
        
        validation_status = 'valid'
        validation_messages = []
        
        # Check daily limits
        daily_total = sum(self.search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '=', self.date),
            ('id', '!=', self.id),
        ]).mapped('unit_amount')) + self.unit_amount
        
        if daily_total > 8:
            validation_status = 'warning'
            validation_messages.append(f"Daily total ({daily_total:.2f} hrs) exceeds recommended 8 hours.")
        
        # Check project allocation if employee_project_allocation module is installed
        if self.env['ir.module.module'].search([
            ('name', '=', 'employee_project_allocation'),
            ('state', '=', 'installed')
        ]):
            self._check_project_allocation(validation_messages)
        
        # Check project access
        if not self._check_project_access():
            validation_status = 'error'
            validation_messages.append("Employee not assigned to this project.")
        
        self.write({
            'validation_status': validation_status,
            'validation_message': '\n'.join(validation_messages) if validation_messages else False,
        })
        
        if validation_status == 'error':
            raise ValidationError('\n'.join(validation_messages))
    
    def _check_project_allocation(self, validation_messages):
        """Check project allocation limits if module is available"""
        try:
            # Get allocation for this employee on this project
            allocation = self.env['project.sale.line.employee.map'].search([
                ('project_id', '=', self.project_id.id),
                ('employee_id', '=', self.employee_id.id),
            ], limit=1)
            
            if allocation and allocation.allocation_percentage > 0:
                # Check if this would exceed allocation
                project_total_logged = sum(self.search([
                    ('employee_id', '=', self.employee_id.id),
                    ('project_id', '=', self.project_id.id),
                    ('id', '!=', self.id),
                ]).mapped('unit_amount')) + self.unit_amount
                
                max_allowed = allocation.allocated_hours
                
                if project_total_logged > max_allowed:
                    validation_messages.append(
                        f"Project allocation exceeded: {project_total_logged:.2f}h / {max_allowed:.2f}h "
                        f"({allocation.allocation_percentage}%)"
                    )
        except Exception:
            # Module not available or other error
            pass
    
    def _check_project_access(self):
        """Check if employee has access to the project"""
        # Check if employee is assigned to project
        if self.employee_id.user_id:
            project_users = self.project_id.message_partner_ids.mapped('user_ids')
            if self.employee_id.user_id in project_users:
                return True
        
        # Check if employee has project allocation (if module available)
        try:
            allocation = self.env['project.sale.line.employee.map'].search([
                ('project_id', '=', self.project_id.id),
                ('employee_id', '=', self.employee_id.id),
            ], limit=1)
            if allocation:
                return True
        except Exception:
            pass
        
        # Check if employee is project manager
        if self.project_id.user_id and self.employee_id.user_id == self.project_id.user_id:
            return True
        
        # For now, allow access (can be made stricter based on requirements)
        return True
    
    @api.onchange('project_id')
    def _onchange_project_id(self):
        """Update task domain when project changes"""
        if self.project_id:
            return {
                'domain': {
                    'task_id': [('project_id', '=', self.project_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'task_id': []
                }
            }
    
    @api.model
    def create(self, vals):
        """Override create to validate on creation"""
        line = super().create(vals)
        line._validate_line()
        return line
    
    def write(self, vals):
        """Override write to validate on update"""
        result = super().write(vals)
        if any(field in vals for field in ['unit_amount', 'date', 'project_id', 'employee_id']):
            for record in self:
                record._validate_line()
        return result
