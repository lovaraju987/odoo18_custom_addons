from odoo import models, fields

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_location = fields.Char("Check-In Location")
    check_out_location = fields.Char("Check-Out Location")
