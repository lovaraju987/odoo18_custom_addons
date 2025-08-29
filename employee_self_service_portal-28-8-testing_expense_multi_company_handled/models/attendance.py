from odoo import models, fields, api
from datetime import datetime, time, timedelta
import logging

_logger = logging.getLogger(__name__)

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_location = fields.Char("Check-In Location")
    check_out_location = fields.Char("Check-Out Location")
    in_latitude = fields.Float("Check-in Latitude", digits=(16, 7))
    in_longitude = fields.Float("Check-in Longitude", digits=(16, 7))
    out_latitude = fields.Float("Check-out Latitude", digits=(16, 7))
    out_longitude = fields.Float("Check-out Longitude", digits=(16, 7))
    is_auto_checkout = fields.Boolean("Auto Check-out", default=False, 
                                    help="Indicates this attendance record was automatically checked out by the system")
    
    # Enhanced computed fields
    worked_hours = fields.Float(
        string='Worked Hours',
        compute='_compute_worked_hours',
        store=True,
        readonly=True
    )
    
    is_late_arrival = fields.Boolean(
        string='Late Arrival',
        compute='_compute_attendance_flags',
        store=True
    )
    
    is_early_departure = fields.Boolean(
        string='Early Departure', 
        compute='_compute_attendance_flags',
        store=True
    )
    
    is_overtime = fields.Boolean(
        string='Overtime',
        compute='_compute_attendance_flags',
        store=True
    )
    
    attendance_status = fields.Selection([
        ('complete', 'Complete'),
        ('active', 'Active'),
        ('late', 'Late Arrival'),
        ('early', 'Early Departure'),
        ('overtime', 'Overtime'),
        ('auto', 'Auto Check-out')
    ], string='Status', compute='_compute_attendance_status', store=True)

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                delta = fields.Datetime.from_string(attendance.check_out) - fields.Datetime.from_string(attendance.check_in)
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = 0.0

    @api.depends('check_in', 'check_out', 'worked_hours')
    def _compute_attendance_flags(self):
        late_threshold = time(9, 30)  # 9:30 AM
        early_threshold = time(17, 30)  # 5:30 PM
        
        for attendance in self:
            # Late arrival check
            if attendance.check_in and attendance.check_in.time() > late_threshold:
                attendance.is_late_arrival = True
            else:
                attendance.is_late_arrival = False
            
            # Early departure check
            if attendance.check_out and attendance.check_out.time() < early_threshold:
                attendance.is_early_departure = True
            else:
                attendance.is_early_departure = False
            
            # Overtime check (more than 8 hours)
            if attendance.worked_hours > 8:
                attendance.is_overtime = True
            else:
                attendance.is_overtime = False

    @api.depends('check_in', 'check_out', 'is_late_arrival', 'is_early_departure', 'is_overtime', 'is_auto_checkout')
    def _compute_attendance_status(self):
        for attendance in self:
            if not attendance.check_out:
                attendance.attendance_status = 'active'
            elif attendance.is_auto_checkout:
                attendance.attendance_status = 'auto'
            elif attendance.is_overtime:
                attendance.attendance_status = 'overtime'
            elif attendance.is_late_arrival:
                attendance.attendance_status = 'late'
            elif attendance.is_early_departure:
                attendance.attendance_status = 'early'
            else:
                attendance.attendance_status = 'complete'
                
    @api.model
    def auto_checkout_employees(self):
        """
        This method is called by the scheduled action (cron job) to automatically check out employees 
        who forgot to check out at the end of the day. 
        The auto-checkout is performed at midnight for any active attendance records from the previous day.
        """
        _logger.info("Running auto-checkout for active attendance records...")
        
        # Find active attendance records from yesterday or earlier
        yesterday = fields.Datetime.now() - timedelta(days=1)
        yesterday_end = yesterday.replace(hour=23, minute=59, second=59)
        
        # Get all active attendance records created before yesterday_end
        active_attendances = self.search([
            ('check_out', '=', False),
            ('check_in', '<=', yesterday_end)
        ])
        
        if not active_attendances:
            _logger.info("No active attendance records found for auto-checkout")
            return
        
        # Auto-checkout these records
        count = 0
        for attendance in active_attendances:
            # Calculate default checkout time (end of work day, 6:00 PM on the same day as check-in)
            checkout_datetime = attendance.check_in.replace(hour=18, minute=0, second=0)
            
            # If check-in was after 6 PM, set check-out 8 hours later (standard workday)
            if attendance.check_in.hour >= 18:
                checkout_datetime = fields.Datetime.from_string(attendance.check_in) + timedelta(hours=8)
            
            try:
                attendance.write({
                    'check_out': checkout_datetime,
                    'is_auto_checkout': True,
                    'check_out_location': 'Auto check-out by system'
                })
                count += 1
                _logger.info(f"Auto checkout for employee {attendance.employee_id.name} (ID: {attendance.employee_id.id})")
            except Exception as e:
                _logger.error(f"Failed to auto-checkout attendance {attendance.id}: {e}")
        
        _logger.info(f"Auto-checkout completed: {count} records processed")
