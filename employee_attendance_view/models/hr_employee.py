from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # Add the attendance_ids field to access attendance records
    attendance_ids = fields.One2many(
        'hr.attendance',
        'employee_id',
        string='Attendance Records'
    )
    
    # def action_open_attendances(self):
    #     """Open the attendance records for this employee"""
    #     self.ensure_one()
    #     return {
    #         'name': f'Attendances: {self.name}',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'hr.attendance',
    #         'view_mode': 'tree,form',
    #         'domain': [('employee_id', '=', self.id)],
    #         'context': {'default_employee_id': self.id},
    #     }
