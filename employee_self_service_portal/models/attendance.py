from odoo import models, fields, api
from datetime import datetime

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_location = fields.Char("Check-In Location")
    check_out_location = fields.Char("Check-Out Location")
    # Ensure worked_hours is present and computed as in Odoo core
    worked_hours = fields.Float(
        string='Worked Hours',
        compute='_compute_worked_hours',
        store=True,
        readonly=True
    )

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                delta = fields.Datetime.from_string(attendance.check_out) - fields.Datetime.from_string(attendance.check_in)
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = 0.0
