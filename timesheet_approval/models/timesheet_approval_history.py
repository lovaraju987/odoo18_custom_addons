# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TimesheetApprovalHistory(models.Model):
    _name = 'timesheet.approval.history'
    _description = 'Timesheet Approval History'
    _order = 'action_date desc, id desc'

    # Parent Reference
    approval_id = fields.Many2one(
        'timesheet.approval',
        string='Timesheet Approval',
        required=True,
        ondelete='cascade',
        help="Parent timesheet approval record"
    )
    
    # Action Information
    action = fields.Selection([
        ('draft', 'Reset to Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Action', required=True,
       help="Action performed on the timesheet")
    
    action_date = fields.Datetime(
        string='Action Date',
        required=True,
        default=fields.Datetime.now,
        help="Date and time of the action"
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        help="User who performed the action"
    )
    
    comments = fields.Text(
        string='Comments',
        help="Additional comments for the action"
    )
    
    # Additional Information
    employee_name = fields.Char(
        string='Employee',
        related='approval_id.employee_id.name',
        store=True,
        help="Employee name for reporting"
    )
    
    manager_name = fields.Char(
        string='Manager',
        related='approval_id.manager_id.name',
        store=True,
        help="Manager name for reporting"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='approval_id.company_id',
        store=True
    )
    
    @api.model
    def get_approval_statistics(self, date_from=None, date_to=None):
        """Get approval statistics for reporting"""
        domain = []
        
        if date_from:
            domain.append(('action_date', '>=', date_from))
        if date_to:
            domain.append(('action_date', '<=', date_to))
        
        records = self.search(domain)
        
        stats = {
            'total_actions': len(records),
            'submissions': len(records.filtered(lambda r: r.action == 'submitted')),
            'approvals': len(records.filtered(lambda r: r.action == 'approved')),
            'rejections': len(records.filtered(lambda r: r.action == 'rejected')),
            'unique_employees': len(set(records.mapped('approval_id.employee_id.id'))),
            'unique_managers': len(set(records.mapped('user_id.id'))),
        }
        
        # Calculate approval rate
        if stats['submissions'] > 0:
            stats['approval_rate'] = (stats['approvals'] / stats['submissions']) * 100
        else:
            stats['approval_rate'] = 0
        
        return stats
