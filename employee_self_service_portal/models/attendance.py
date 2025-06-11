from odoo import models, fields

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    in_latitude = fields.Char("Check-In Latitude")
    in_longitude = fields.Char("Check-In Longitude")
    out_latitude = fields.Char("Check-Out Latitude")
    out_longitude = fields.Char("Check-Out Longitude")
    check_in_location = fields.Char("Check-In Location")
    check_out_location = fields.Char("Check-Out Location")
