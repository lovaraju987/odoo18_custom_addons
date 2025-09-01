# controllers/main.py
from odoo import http, fields
from odoo.http import request
from .access_helpers import check_portal_access, has_feature_access
import html
import json
import logging

# Set up logger
_logger = logging.getLogger(__name__)

# Constants for model names and URLs
CRM_TAG_MODEL = 'crm.tag'
CRM_REDIRECT_URL = '/my/employee/crm'
HR_EMPLOYEE_MODEL = 'hr.employee'
HR_ATTENDANCE_MODEL = 'hr.attendance'
CRM_LEAD_MODEL = 'crm.lead'
CRM_STAGE_MODEL = 'crm.stage'
MY_EMPLOYEE_URL = '/my/employee'

def get_user_timezone():
    """Get the user's timezone (or fallback to company or UTC)."""
    import pytz
    user_tz = request.env.user.tz or request.env.company.timezone or 'UTC'
    return user_tz

def get_local_datetime(dt=None):
    """Convert UTC datetime to user's local timezone."""
    import pytz
    from datetime import datetime
    
    if dt is None:
        dt = datetime.now()
    
    user_tz = get_user_timezone()
    user_pytz = pytz.timezone(user_tz)
    
    if hasattr(dt, 'tzinfo') and dt.tzinfo:
        # If datetime already has tzinfo, convert to user timezone
        return dt.astimezone(user_pytz)
    else:
        # Assume the datetime is UTC if no tzinfo
        utc_dt = dt.replace(tzinfo=pytz.UTC)
        return utc_dt.astimezone(user_pytz)

def _process_tag_ids(post):
    """Refactored to reduce cognitive complexity."""
    tag_ids = []
    # Get tag ids from post (handle both list and string cases)
    if hasattr(post, 'getlist'):
        tag_ids = post.getlist('tag_ids[]') or post.getlist('tag_ids')
    else:
        tag_ids = post.get('tag_ids[]', []) or post.get('tag_ids', [])
        if isinstance(tag_ids, str):
            tag_ids = tag_ids.split(',') if ',' in tag_ids else [tag_ids]
    if not isinstance(tag_ids, list):
        tag_ids = [tag_ids]
    tag_id_list = []
    for tag in tag_ids or []:
        if not tag:
            continue
        try:
            tag_id_list.append(int(tag))
        except (ValueError, TypeError):
            tag_rec = request.env[CRM_TAG_MODEL].sudo().search([('name', '=', tag)], limit=1)
            if not tag_rec:
                tag_rec = request.env[CRM_TAG_MODEL].sudo().create({'name': tag})
            tag_id_list.append(tag_rec.id)
    tag_id_list = [int(t) for t in tag_id_list if t]
    import logging
    _logger = logging.getLogger(__name__)
    _logger.info('ESS Portal: tag_id_list to write: %s', tag_id_list)
    return tag_id_list

def _process_partner_field(field_value, field_name='partner_id'):
    """Process partner field - handle existing IDs or create new partners."""
    if not field_value:
        return False
    
    # Try to convert to int (existing partner ID)
    try:
        partner_id = int(field_value)
        # Verify partner exists
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if partner.exists():
            return partner_id
    except (ValueError, TypeError):
        pass
    
    # Field value is a string - create new partner
    if isinstance(field_value, str) and field_value.strip():
        partner_name = field_value.strip()
        
        # Check if partner already exists by name
        existing_partner = request.env['res.partner'].sudo().search([
            ('name', '=ilike', partner_name)
        ], limit=1)
        
        if existing_partner:
            return existing_partner.id
        
        # Create new partner
        partner_vals = {'name': partner_name}
        
        # For point of contact, set as individual (not company)
        if field_name == 'point_of_contact_id':
            partner_vals['is_company'] = False
        else:
            # For main customer, default to company
            partner_vals['is_company'] = True
            
        new_partner = request.env['res.partner'].sudo().create(partner_vals)
        
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info('ESS Portal: Created new partner: %s (ID: %s)', partner_name, new_partner.id)
        
        return new_partner.id
    
    return False

class PortalEmployee(http.Controller):
    def _get_employee(self):
        return request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)

    @http.route(MY_EMPLOYEE_URL, type='http', auth='user', website=True)
    def portal_employee_profile(self, **kw):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        return request.render('employee_self_service_portal.portal_employee_profile_personal', {
            'employee': employee,
            'section': 'personal',
        })

    @http.route(MY_EMPLOYEE_URL + '/attendance/checkin', type='http', auth='user', methods=['POST'], website=True)
    def check_in(self, **post):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect(MY_EMPLOYEE_URL + '?error=employee_not_found')
        
        # Enhanced validation and duplicate prevention
        try:
            # Check for existing open attendance
            existing_attendance = request.env[HR_ATTENDANCE_MODEL].sudo().search([
                ('employee_id', '=', employee.id),
                ('check_out', '=', False)
            ], limit=1)
            
            if existing_attendance:
                return request.redirect(MY_EMPLOYEE_URL + '/attendance?error=already_checked_in')
            
            # Validate check-in time (business hours)
            from datetime import datetime
            import pytz
            
            # Get user's timezone (or use company timezone as fallback)
            user_tz = request.env.user.tz or request.env.company.timezone or 'UTC'
            user_pytz = pytz.timezone(user_tz)
            
            # Get current time in user's timezone
            utc_now = datetime.now(pytz.UTC)
            local_now = utc_now.astimezone(user_pytz)
            current_time = local_now.time()
            
            # Basic business hours validation (6 AM to 11 PM)
            from datetime import time
            min_time = time(6, 0)  # 6:00 AM
            max_time = time(23, 0)  # 11:00 PM
            
            if not (min_time <= current_time <= max_time):
                return request.redirect(MY_EMPLOYEE_URL + '/attendance?error=invalid_time')
            
            # Location and other data
            in_latitude = post.get('in_latitude')
            in_longitude = post.get('in_longitude')
            check_in_location = post.get('check_in_location')
            
            # Log location data for debugging
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info(f"Check-in location data - lat: {in_latitude}, long: {in_longitude}, location: {check_in_location}")
            _logger.info(f"User timezone: {user_tz}, Local time: {local_now}")
            
            # Check if it's a late arrival (after 9:30 AM)
            late_threshold = time(9, 30)
            is_late = current_time > late_threshold
            
            # If no location is provided, try to get a default one
            if not check_in_location:
                check_in_location = post.get('location') or 'Check-in from Portal'
            
            # Use user's timezone to properly record time
            # Use format_datetime to create a datetime string with timezone info
            local_check_in = fields.Datetime.context_timestamp(request.env.user, fields.Datetime.now())
            
            vals = {
                'employee_id': employee.id,
                'check_in': fields.Datetime.now(),  # Server will convert this appropriately
                'check_in_location': check_in_location,
            }
            
            # Make sure we convert latitude/longitude to float if provided
            try:
                if in_latitude:
                    vals['in_latitude'] = float(in_latitude)
                if in_longitude:
                    vals['in_longitude'] = float(in_longitude)
            except (ValueError, TypeError):
                _logger.warning(f"Invalid latitude/longitude values: {in_latitude}, {in_longitude}")
                
            # Create attendance record
            attendance = request.env[HR_ATTENDANCE_MODEL].sudo().create(vals)
            
            # Log successful check-in
            _logger.info(f"Check-in successful for employee {employee.name} at {local_now}")
            
            return request.redirect(MY_EMPLOYEE_URL + '/attendance?success=checked_in')
            
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Check-in failed: %s", e)
            return request.redirect(MY_EMPLOYEE_URL + '/attendance?error=checkin_failed')
        
    @http.route(MY_EMPLOYEE_URL + '/attendance/quick-checkin', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def quick_check_in(self, **post):
        """Quick check-in from dashboard"""
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.make_response(json.dumps({'status': 'error', 'message': 'Employee not found'}), 
                                       headers={'Content-Type': 'application/json'})
        
        try:
            # REMOVED: Check for existing open attendance
            # We now allow multiple check-ins per day, so we don't need to validate
            # if there's an existing open attendance
            
            # Validate check-in time (business hours) - consistent with attendance page logic
            from datetime import datetime, time
            now = datetime.now()
            current_time = now.time()
            
            # Basic business hours validation (6 AM to 11 PM)
            min_time = time(6, 0)  # 6:00 AM
            max_time = time(23, 0)  # 11:00 PM
            
            if not (min_time <= current_time <= max_time):
                return request.make_response(json.dumps({
                    'status': 'error', 
                    'message': 'Check-in not allowed at this time (6 AM - 11 PM only)'
                }), headers={'Content-Type': 'application/json'})
            
            # Get location data from POST request
            in_latitude = post.get('in_latitude')
            in_longitude = post.get('in_longitude')
            check_in_location = post.get('check_in_location') or post.get('location') or 'Quick Check-in from Dashboard'
            
            # Create attendance record
            vals = {
                'employee_id': employee.id,
                'check_in': fields.Datetime.now(),
                'check_in_location': check_in_location,
            }
            
            # Make sure we convert latitude/longitude to float if provided
            try:
                if in_latitude:
                    vals['in_latitude'] = float(in_latitude)
                if in_longitude:
                    vals['in_longitude'] = float(in_longitude)
            except (ValueError, TypeError):
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning(f"Invalid quick check-in latitude/longitude values: {in_latitude}, {in_longitude}")
            
            attendance = request.env[HR_ATTENDANCE_MODEL].sudo().create(vals)
            
            # Log successful check-in
            _logger.info(f"Quick check-in successful for employee {employee.name} at {now}")
            
            return request.make_response(json.dumps({'status': 'success', 'message': 'Checked in successfully'}), 
                                       headers={'Content-Type': 'application/json'})
            
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Quick check-in failed: %s", e)
            return request.make_response(json.dumps({'status': 'error', 'message': 'Check-in failed'}), 
                                       headers={'Content-Type': 'application/json'})

    @http.route(MY_EMPLOYEE_URL + '/attendance/checkout', type='http', auth='user', methods=['POST'], website=True)
    def check_out(self, **post):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect(MY_EMPLOYEE_URL + '?error=employee_not_found')
            
        try:
            # Find the last open attendance record
            last_attendance = request.env[HR_ATTENDANCE_MODEL].sudo().search([
                ('employee_id', '=', employee.id),
                ('check_out', '=', False)
            ], order='check_in desc', limit=1)
            
            if not last_attendance:
                return request.redirect(MY_EMPLOYEE_URL + '/attendance?error=no_checkin_found')
            
            # Validate minimum work duration (at least 30 minutes)
            from datetime import datetime, timedelta
            import pytz
            
            # Get user's timezone (or use company timezone as fallback)
            user_tz = request.env.user.tz or request.env.company.timezone or 'UTC'
            user_pytz = pytz.timezone(user_tz)
            
            # Get current time in user's timezone
            utc_now = datetime.now(pytz.UTC)
            local_now = utc_now.astimezone(user_pytz)
            
            check_in_time = fields.Datetime.from_string(last_attendance.check_in)
            
            # Convert check_in_time to user timezone for proper comparison
            check_in_time_local = check_in_time.replace(tzinfo=pytz.UTC).astimezone(user_pytz)
            
            # Re-enabled 30-minute validation
            min_duration = timedelta(minutes=30)
            if (local_now - check_in_time_local) < min_duration:
                return request.redirect(MY_EMPLOYEE_URL + '/attendance?error=minimum_duration_not_met')
            
            # Location and other data
            out_latitude = post.get('out_latitude')
            out_longitude = post.get('out_longitude')
            check_out_location = post.get('check_out_location')
            
            # Log location data for debugging
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info(f"Check-out location data - lat: {out_latitude}, long: {out_longitude}, location: {check_out_location}")
            _logger.info(f"User timezone: {user_tz}, Local time: {local_now}")
            
            # Check if it's an early departure (before 5:30 PM)
            from datetime import time
            early_threshold = time(17, 30)
            current_time = local_now.time()
            is_early_departure = current_time < early_threshold
            
            # If no location is provided, try to get a default one
            if not check_out_location:
                check_out_location = post.get('location') or 'Check-out from Portal'
            
            # Use format_datetime to create a datetime string with timezone info
            local_check_out = fields.Datetime.context_timestamp(request.env.user, fields.Datetime.now())
            
            vals = {
                'check_out': fields.Datetime.now(),  # Server will convert this appropriately
                'check_out_location': check_out_location,
                'is_auto_checkout': False,  # Explicit manual checkout
            }
            
            # Make sure we convert latitude/longitude to float if provided
            try:
                if out_latitude:
                    vals['out_latitude'] = float(out_latitude)
                if out_longitude:
                    vals['out_longitude'] = float(out_longitude)
            except (ValueError, TypeError):
                _logger.warning(f"Invalid latitude/longitude values: {out_latitude}, {out_longitude}")
                
            # Update attendance record
            last_attendance.sudo().write(vals)
            
            # Re-browse to get updated computed fields
            updated_attendance = request.env[HR_ATTENDANCE_MODEL].sudo().browse(last_attendance.id)
            
            # Log successful check-out with worked hours
            _logger.info(f"Check-out successful for employee {employee.name}. Worked hours: {updated_attendance.worked_hours}")
            
            return request.redirect(MY_EMPLOYEE_URL + '/attendance?success=checked_out')
            
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Check-out failed: %s", e)
            return request.redirect(MY_EMPLOYEE_URL + '/attendance?error=checkout_failed')

    @http.route(MY_EMPLOYEE_URL + '/attendance/quick-checkout', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def quick_check_out(self, **post):
        """Quick check-out from dashboard"""
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.make_response(json.dumps({'status': 'error', 'message': 'Employee not found'}), 
                                       headers={'Content-Type': 'application/json'})
        
        try:
            # Find the last open attendance record
            last_attendance = request.env[HR_ATTENDANCE_MODEL].sudo().search([
                ('employee_id', '=', employee.id),
                ('check_out', '=', False)
            ], order='check_in desc', limit=1)
            
            if not last_attendance:
                return request.make_response(json.dumps({'status': 'error', 'message': 'No active check-in found'}), 
                                           headers={'Content-Type': 'application/json'})
            
            # Validate minimum work duration (at least 30 minutes)
            from datetime import datetime, timedelta
            import pytz
            
            # Get user's timezone (or use company timezone as fallback)
            user_tz = request.env.user.tz or request.env.company.timezone or 'UTC'
            user_pytz = pytz.timezone(user_tz)
            
            # Get current time in user's timezone
            utc_now = datetime.now(pytz.UTC)
            local_now = utc_now.astimezone(user_pytz)
            
            check_in_time = fields.Datetime.from_string(last_attendance.check_in)
            
            # Convert check_in_time to user timezone for proper comparison
            check_in_time_local = check_in_time.replace(tzinfo=pytz.UTC).astimezone(user_pytz)
            
            # Re-enabled 30-minute validation
            min_duration = timedelta(minutes=30)
            if (local_now - check_in_time_local) < min_duration:
                return request.make_response(json.dumps({
                    'status': 'error', 
                    'message': 'Minimum work duration not met (30 minutes required)'
                }), headers={'Content-Type': 'application/json'})
            
            # Get location data from POST request
            out_latitude = post.get('out_latitude')
            out_longitude = post.get('out_longitude')
            check_out_location = post.get('check_out_location') or post.get('location') or 'Quick Check-out from Dashboard'
            
            # Update attendance record
            vals = {
                'check_out': fields.Datetime.now(),
                'check_out_location': check_out_location,
                'is_auto_checkout': False,  # Explicit manual checkout
            }
            
            # Make sure we convert latitude/longitude to float if provided
            try:
                if out_latitude:
                    vals['out_latitude'] = float(out_latitude)
                if out_longitude:
                    vals['out_longitude'] = float(out_longitude)
            except (ValueError, TypeError):
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning(f"Invalid quick check-out latitude/longitude values: {out_latitude}, {out_longitude}")
            
            last_attendance.sudo().write(vals)
            
            # Get worked hours
            updated_attendance = request.env[HR_ATTENDANCE_MODEL].sudo().browse(last_attendance.id)
            worked_hours = round(updated_attendance.worked_hours, 2)
            
            return request.make_response(json.dumps({
                'status': 'success', 
                'message': f'Checked out successfully. Worked {worked_hours} hours'
            }), headers={'Content-Type': 'application/json'})
            
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Quick check-out failed: %s", e)
            return request.make_response(json.dumps({'status': 'error', 'message': 'Check-out failed'}), 
                                       headers={'Content-Type': 'application/json'})
    
    @http.route(MY_EMPLOYEE_URL + '/attendance', type='http', auth='user', website=True)
    @check_portal_access('attendance')
    def portal_attendance_history(self, **kwargs):
        from datetime import datetime
        import pytz
        
        # Get user's timezone
        user_timezone = get_user_timezone()
        user_pytz = pytz.timezone(user_timezone)
        
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        
        # Get current time in user's timezone
        utc_now = datetime.now(pytz.UTC)
        local_now = utc_now.astimezone(user_pytz)
        
        # Use current month/year as default if not provided
        month = int(kwargs.get('month', local_now.month))
        year = int(kwargs.get('year', local_now.year))
        
        domain = [('employee_id', '=', employee.id)]
        if month and year:
            from calendar import monthrange
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)
            domain += [('check_in', '>=', start_date.strftime('%Y-%m-%d 00:00:00')),
                       ('check_in', '<=', end_date.strftime('%Y-%m-%d 23:59:59'))]
        
        attendances = request.env[HR_ATTENDANCE_MODEL].sudo().search(
            domain, order='check_in desc', limit=50)  # Increased limit for better analytics
        
        today_att = None
        today_str = local_now.strftime('%Y-%m-%d')
        
        # Find today's attendance based on user's timezone
        for att in attendances:
            if att.check_in:
                check_in_local = fields.Datetime.context_timestamp(request.env.user, att.check_in)
                if check_in_local.strftime('%Y-%m-%d') == today_str:
                    today_att = att
                    break
        
        # Enhanced analytics
        analytics_data = self._get_attendance_analytics(employee, month, year)
        
        # For dropdowns
        current_year = local_now.year
        years = list(range(current_year - 5, current_year + 2))
        months = [
            {'value': i, 'name': datetime(2000, i, 1).strftime('%B')} for i in range(1, 13)
        ]
        
        # Status messages
        success_message = None
        error_message = None
        
        if kwargs.get('success') == 'checked_in':
            success_message = "Successfully checked in!"
        elif kwargs.get('success') == 'checked_out':
            success_message = "Successfully checked out!"
        elif kwargs.get('error') == 'already_checked_in':
            error_message = "You are already checked in. Please check out first."
        elif kwargs.get('error') == 'no_checkin_found':
            error_message = "No active check-in found."
        elif kwargs.get('error') == 'invalid_time':
            error_message = f"Check-in not allowed at this time (6 AM - 11 PM only). Your local time: {local_now.strftime('%I:%M %p')} ({user_timezone})."
        elif kwargs.get('error') == 'minimum_duration_not_met':
            error_message = "Minimum work duration not met (30 minutes required)."
        elif kwargs.get('error'):
            error_message = "An error occurred. Please try again."
        
        return request.render('employee_self_service_portal.portal_attendance', {
            'attendances': attendances,
            'employee': employee,
            'today_att': today_att,
            'selected_month': month,
            'selected_year': year,
            'years': years,
            'months': months,
            'analytics': analytics_data,
            'success_message': success_message,
            'error_message': error_message,
            'user_timezone': user_timezone,
            'format_datetime': lambda dt: fields.Datetime.context_timestamp(request.env.user, dt).strftime('%I:%M %p') if dt else '',
            'format_date': lambda dt: fields.Datetime.context_timestamp(request.env.user, dt).strftime('%d/%m/%Y') if dt else '',
            'format_day': lambda dt: fields.Datetime.context_timestamp(request.env.user, dt).strftime('%A') if dt else '',
        })

    def _get_attendance_analytics(self, employee, month, year):
        """Calculate comprehensive attendance analytics with timezone awareness"""
        from datetime import datetime, timedelta, time
        from calendar import monthrange
        from collections import defaultdict
        import pytz
        
        # Get user's timezone
        user_timezone = get_user_timezone()
        user_pytz = pytz.timezone(user_timezone)
        
        # Date range for the selected month in user's timezone
        start_date = datetime(year, month, 1, tzinfo=user_pytz)
        last_day = monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59, tzinfo=user_pytz)
        
        # Convert to UTC for database query
        start_date_utc = start_date.astimezone(pytz.UTC)
        end_date_utc = end_date.astimezone(pytz.UTC)
        
        # Get all attendance records for the month
        attendances = request.env[HR_ATTENDANCE_MODEL].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', start_date_utc),
            ('check_in', '<=', end_date_utc)
        ])
        
        # Group attendances by day for accurate day counting (using local timezone)
        attendance_by_day = defaultdict(list)
        for att in attendances:
            # Convert check_in time to user's timezone for day grouping
            check_in_local = fields.Datetime.context_timestamp(request.env.user, att.check_in)
            day_key = check_in_local.strftime('%Y-%m-%d')
            attendance_by_day[day_key].append(att)
        
        # Calculate metrics
        total_days = len(attendance_by_day)  # Unique days with attendance
        
        # Calculate total hours per day and then sum them up
        total_hours = 0
        for day, day_attendances in attendance_by_day.items():
            day_hours = sum(att.worked_hours for att in day_attendances if att.worked_hours)
            total_hours += day_hours
            
        avg_hours = total_hours / total_days if total_days > 0 else 0
        
        # Calculate late arrivals by day - only count one late arrival per day
        # Define late threshold (9:30 AM)
        late_threshold = time(9, 30)
        late_arrivals = 0
        
        for day, day_attendances in attendance_by_day.items():
            # Sort by check-in time to get the first check-in of the day
            day_attendances.sort(key=lambda x: x.check_in)
            # Convert check-in time to user's timezone
            first_check_in = fields.Datetime.context_timestamp(request.env.user, day_attendances[0].check_in)
            # Check if first check-in of the day was late
            if first_check_in.time() > late_threshold:
                late_arrivals += 1
        
        # Working days in month (excluding weekends)
        working_days = 0
        current_date = start_date.date()
        while current_date <= end_date.date():
            if current_date.weekday() < 5:  # Monday=0, Sunday=6
                working_days += 1
            current_date += timedelta(days=1)
        
        # Attendance percentage
        attendance_percentage = (total_days / working_days * 100) if working_days > 0 else 0
        
        # Early departures (before 5:30 PM) - count only days with early departure
        early_threshold = time(17, 30)
        early_departures = 0
        
        for day, day_attendances in attendance_by_day.items():
            # Check if any attendance records for the day had an early departure
            early_departure = False
            for att in day_attendances:
                if att.check_out:
                    # Convert check-out time to user's timezone
                    check_out_local = fields.Datetime.context_timestamp(request.env.user, att.check_out)
                    if check_out_local.time() < early_threshold:
                        early_departure = True
                        break
            if early_departure:
                early_departures += 1
        
        # Overtime (more than 8.5 hours per day)
        overtime_days = 0
        for day, day_attendances in attendance_by_day.items():
            day_hours = sum(att.worked_hours for att in day_attendances if att.worked_hours)
            if day_hours > 8.5:
                overtime_days += 1
        
        # This week's data
        # Get current time in user's timezone
        utc_now = datetime.now(pytz.UTC)
        local_now = utc_now.astimezone(user_pytz)
        
        # Calculate week start in user's timezone
        week_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=local_now.weekday())
        week_start_utc = week_start.astimezone(pytz.UTC)
        
        week_attendances = request.env[HR_ATTENDANCE_MODEL].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', week_start_utc),
            ('check_in', '<=', utc_now)
        ])
        
        # Group week attendances by day for consistent calculation
        week_attendance_by_day = defaultdict(list)
        for att in week_attendances:
            # Convert check_in time to user's timezone for day grouping
            check_in_local = fields.Datetime.context_timestamp(request.env.user, att.check_in)
            day_key = check_in_local.strftime('%Y-%m-%d')
            week_attendance_by_day[day_key].append(att)
        
        # Calculate total hours per day and then sum them up
        this_week_hours = 0
        for day, day_attendances in week_attendance_by_day.items():
            day_hours = sum(att.worked_hours for att in day_attendances if att.worked_hours)
            this_week_hours += day_hours
        
        return {
            'total_days': total_days,
            'total_hours': round(total_hours, 2),
            'avg_hours': round(avg_hours, 2),
            'working_days': working_days,
            'attendance_percentage': round(attendance_percentage, 1),
            'late_arrivals': late_arrivals,
            'early_departures': early_departures,
            'overtime_days': overtime_days,
            'this_week_hours': round(this_week_hours, 2),
            'month_name': datetime(year, month, 1).strftime('%B %Y')
        }

    @http.route(MY_EMPLOYEE_URL + '/attendance/analytics', type='http', auth='user', website=True)
    def portal_attendance_analytics(self, **kwargs):
        """Dedicated analytics page for attendance"""
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect(MY_EMPLOYEE_URL)
        
        from datetime import datetime
        import pytz
        
        # Get user's timezone
        user_timezone = get_user_timezone()
        user_pytz = pytz.timezone(user_timezone)
        
        # Get current time in user's timezone
        utc_now = datetime.now(pytz.UTC)
        local_now = utc_now.astimezone(user_pytz)
        
        # Get analytics for current month and last 3 months
        analytics_months = []
        for i in range(4):
            from datetime import timedelta
            month_date = local_now.replace(day=1) - timedelta(days=i*30)
            month_analytics = self._get_attendance_analytics(employee, month_date.month, month_date.year)
            analytics_months.append(month_analytics)
        
        return request.render('employee_self_service_portal.portal_attendance_analytics', {
            'employee': employee,
            'analytics_months': analytics_months,
            'current_month': analytics_months[0] if analytics_months else {},
            'user_timezone': user_timezone,
            'format_datetime': lambda dt: fields.Datetime.context_timestamp(request.env.user, dt).strftime('%I:%M %p') if dt else '',
            'format_date': lambda dt: fields.Datetime.context_timestamp(request.env.user, dt).strftime('%d/%m/%Y') if dt else '',
            'format_day': lambda dt: fields.Datetime.context_timestamp(request.env.user, dt).strftime('%A') if dt else '',
        })

    @http.route(MY_EMPLOYEE_URL + '/attendance/export', type='http', auth='user', website=True)
    def portal_attendance_export(self, **kwargs):
        """Export attendance data to Excel"""
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect(MY_EMPLOYEE_URL)
        
        try:
            import io
            import xlsxwriter
            from datetime import datetime, timedelta, time
            
            # Get date range (default: current month)
            now = datetime.now()
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            
            if not start_date:
                start_date = now.replace(day=1).strftime('%Y-%m-%d')
            if not end_date:
                from calendar import monthrange
                last_day = monthrange(now.year, now.month)[1]
                end_date = now.replace(day=last_day).strftime('%Y-%m-%d')
            
            # Get attendance data
            attendances = request.env[HR_ATTENDANCE_MODEL].sudo().search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', start_date + ' 00:00:00'),
                ('check_in', '<=', end_date + ' 23:59:59')
            ], order='check_in desc')
            
            # Create Excel file
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Attendance Report')
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })
            
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            time_format = workbook.add_format({'num_format': 'hh:mm AM/PM'})
            hours_format = workbook.add_format({'num_format': '0.00'})
            
            # Headers
            headers = [
                'Date', 'Day', 'Check-In Time', 'Check-In Location', 
                'Check-Out Time', 'Check-Out Location', 'Worked Hours', 'Status'
            ]
            
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # Data rows
            for row, att in enumerate(attendances, 1):
                check_in_date = att.check_in.date() if att.check_in else None
                day_name = att.check_in.strftime('%A') if att.check_in else ''
                check_in_time = att.check_in.time() if att.check_in else None
                check_out_time = att.check_out.time() if att.check_out else None
                
                # Determine status
                status = 'Complete' if att.check_out else 'Active'
                if att.check_in and att.check_in.time() > time(9, 30):
                    status += ' (Late)'
                if att.check_out and att.check_out.time() < time(17, 30):
                    status += ' (Early)'
                
                worksheet.write(row, 0, check_in_date, date_format)
                worksheet.write(row, 1, day_name)
                worksheet.write(row, 2, check_in_time, time_format)
                worksheet.write(row, 3, att.check_in_location or '')
                worksheet.write(row, 4, check_out_time, time_format)
                worksheet.write(row, 5, att.check_out_location or '')
                worksheet.write(row, 6, att.worked_hours or 0, hours_format)
                worksheet.write(row, 7, status)
            
            # Summary section
            summary_row = len(attendances) + 3
            worksheet.write(summary_row, 0, 'SUMMARY', header_format)
            worksheet.write(summary_row + 1, 0, 'Total Days:')
            worksheet.write(summary_row + 1, 1, len(attendances))
            worksheet.write(summary_row + 2, 0, 'Total Hours:')
            worksheet.write(summary_row + 2, 1, sum(att.worked_hours for att in attendances if att.worked_hours), hours_format)
            worksheet.write(summary_row + 3, 0, 'Average Hours/Day:')
            avg_hours = sum(att.worked_hours for att in attendances if att.worked_hours) / len(attendances) if attendances else 0
            worksheet.write(summary_row + 3, 1, avg_hours, hours_format)
            
            # Auto-adjust column widths
            worksheet.set_column('A:A', 12)  # Date
            worksheet.set_column('B:B', 10)  # Day
            worksheet.set_column('C:C', 15)  # Check-in time
            worksheet.set_column('D:D', 30)  # Check-in location
            worksheet.set_column('E:E', 15)  # Check-out time
            worksheet.set_column('F:F', 30)  # Check-out location
            worksheet.set_column('G:G', 12)  # Worked hours
            worksheet.set_column('H:H', 15)  # Status
            
            workbook.close()
            output.seek(0)
            
            # Generate filename
            filename = f"attendance_report_{employee.name}_{start_date}_to_{end_date}.xlsx"
            filename = filename.replace(' ', '_').replace('/', '-')
            
            # Return file
            return request.make_response(
                output.getvalue(),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', f'attachment; filename="{filename}"')
                ]
            )
            
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Attendance export failed: %s", e)
            return request.redirect(MY_EMPLOYEE_URL + '/attendance?error=export_failed')

    @http.route(MY_EMPLOYEE_URL + '/edit', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_edit(self, **post):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect(MY_EMPLOYEE_URL)
        if http.request.httprequest.method == 'POST':
            vals = {}
            # Personal Details
            vals['work_email'] = post.get('work_email')
            vals['work_phone'] = post.get('work_phone')
            vals['birthday'] = post.get('birthday')
            vals['gender'] = post.get('gender')
            vals['marital'] = post.get('marital')
            # Experience & Skills
            vals['x_experience'] = post.get('x_experience')
            vals['x_skills'] = post.get('x_skills')
            # Certifications
            vals['x_certifications'] = post.get('x_certifications')
            # Bank Details
            vals['x_bank_account'] = post.get('x_bank_account')
            vals['x_bank_name'] = post.get('x_bank_name')
            vals['x_ifsc'] = post.get('x_ifsc')
            # Only update fields that are present in the form
            vals = {k: v for k, v in vals.items() if v is not None}
            if vals:
                employee.sudo().write(vals)
            return request.redirect(MY_EMPLOYEE_URL)
        return request.render('employee_self_service_portal.portal_employee_edit', {
            'employee': employee,
        })

    @http.route('/my/ess', type='http', auth='user', website=True)
    def portal_ess_dashboard(self, **kwargs):
        # Set enhanced dashboard as default
        return self._render_ess_dashboard('employee_self_service_portal.portal_ess_dashboard_enhanced', **kwargs)

    @http.route('/my/ess/classic', type='http', auth='user', website=True)  
    def portal_ess_dashboard_classic(self, **kwargs):
        # Keep the classic view accessible via /my/ess/classic
        return self._render_ess_dashboard('employee_self_service_portal.portal_ess_dashboard', **kwargs)
        
    @http.route('/my/ess/enhanced', type='http', auth='user', website=True)  
    def portal_ess_dashboard_enhanced(self, **kwargs):
        # Maintain this route for backward compatibility
        return self._render_ess_dashboard('employee_self_service_portal.portal_ess_dashboard_enhanced', **kwargs)

    def _render_ess_dashboard(self, template_name, **kwargs):
        """Common method to render dashboard with enhanced data"""
        import pytz
        
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        
        # Get dashboard statistics
        dashboard_data = {}
        
        if employee:
            # Enhanced dashboard data with more detailed analytics
            dashboard_data = self._get_enhanced_dashboard_data(employee)
            
            # Add feature access permissions
            dashboard_data.update({
                'has_attendance_access': has_feature_access('attendance'),
                'has_crm_access': has_feature_access('crm'),
                'has_expenses_access': has_feature_access('expenses'),
                'has_payslip_access': has_feature_access('payslip')
            })
        
        # Add view type for enhanced template
        dashboard_data['view_type'] = 'enhanced' if 'enhanced' in template_name else 'standard'
        
        # Add timezone-aware formatting functions
        user_timezone = get_user_timezone()
        dashboard_data.update({
            'user_timezone': user_timezone,
            'format_datetime': lambda dt: fields.Datetime.context_timestamp(request.env.user, dt).strftime('%I:%M %p') if dt else '',
            'format_date': lambda dt: fields.Datetime.context_timestamp(request.env.user, dt).strftime('%d/%m/%Y') if dt else '',
            'format_day': lambda dt: fields.Datetime.context_timestamp(request.env.user, dt).strftime('%A') if dt else '',
        })
        
        return request.render(template_name, dashboard_data)

    def _get_enhanced_dashboard_data(self, employee):
        """Get comprehensive dashboard data for enhanced view"""
        from datetime import date, datetime, timedelta
        
        # Basic employee data
        dashboard_data = {'employee': employee}
        
        # Payslips data with enhanced analytics
        payslips = request.env['hr.payslip'].sudo().search([
            ('employee_id', '=', employee.id)
        ])
        payslips_count = len(payslips)
        
        # Latest payslip
        latest_payslip = request.env['hr.payslip'].sudo().search([
            ('employee_id', '=', employee.id),
            ('state', 'in', ['done', 'paid'])
        ], order='date_from desc', limit=1)
        
        # Enhanced attendance data - get ALL attendance records for today using user's timezone
        import pytz
        
        # Get user's timezone
        user_timezone = get_user_timezone()
        user_pytz = pytz.timezone(user_timezone)
        
        # Get current time in user's timezone
        utc_now = datetime.now(pytz.UTC)
        local_now = utc_now.astimezone(user_pytz)
        today_local = local_now.date()
        
        # Calculate today start and end in user's local timezone, then convert to UTC for database query
        local_day_start = datetime.combine(today_local, datetime.min.time()).replace(tzinfo=user_pytz)
        local_day_end = datetime.combine(today_local, datetime.max.time()).replace(tzinfo=user_pytz)
        
        # Convert to UTC for database query
        utc_day_start = local_day_start.astimezone(pytz.UTC)
        utc_day_end = local_day_end.astimezone(pytz.UTC)
        
        today_attendances = request.env[HR_ATTENDANCE_MODEL].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', utc_day_start),
            ('check_in', '<=', utc_day_end)
        ])
        
        # Weekly attendance summary in user's timezone
        week_start_local = today_local - timedelta(days=today_local.weekday())
        week_end_local = week_start_local + timedelta(days=6)
        
        # Convert to datetime with timezone
        week_start_dt = datetime.combine(week_start_local, datetime.min.time()).replace(tzinfo=user_pytz)
        week_end_dt = datetime.combine(week_end_local, datetime.max.time()).replace(tzinfo=user_pytz)
        
        # Convert to UTC for database query
        utc_week_start = week_start_dt.astimezone(pytz.UTC)
        utc_week_end = week_end_dt.astimezone(pytz.UTC)
        
        week_attendance = request.env[HR_ATTENDANCE_MODEL].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', utc_week_start),
            ('check_in', '<=', utc_week_end)
        ])
        
        # Calculate weekly hours using the day grouping approach for consistency
        from collections import defaultdict
        week_attendance_by_day = defaultdict(list)
        for att in week_attendance:
            day_key = att.check_in.strftime('%Y-%m-%d')
            week_attendance_by_day[day_key].append(att)
        
        # Calculate total hours per day and then sum them up
        weekly_hours = 0
        for day, day_attendances in week_attendance_by_day.items():
            day_hours = sum(att.worked_hours for att in day_attendances if att.worked_hours)
            weekly_hours += day_hours
        
        # Enhanced CRM data
        user = request.env.user
        crm_leads = request.env[CRM_LEAD_MODEL].sudo().search([('user_id', '=', user.id)])
        crm_leads_count = len(crm_leads)
        
        # CRM analytics
        new_leads = crm_leads.filtered(lambda l: l.stage_id.name in ['New', 'Qualification'] if l.stage_id else False)
        won_leads = crm_leads.filtered(lambda l: l.stage_id.name == 'Won' if l.stage_id else False)
        total_revenue = sum(crm_leads.mapped('expected_revenue'))
        
        # Enhanced Expense statistics
        today_dt = datetime.now().date()
        first_day_month = today_dt.replace(day=1)
        
        current_month_expenses = request.env['hr.expense'].sudo().search([
            ('employee_id', '=', employee.id),
            ('date', '>=', first_day_month),
            ('date', '<=', today_dt)
        ])
        
        # Year-to-date expenses
        year_start = today_dt.replace(month=1, day=1)
        ytd_expenses = request.env['hr.expense'].sudo().search([
            ('employee_id', '=', employee.id),
            ('date', '>=', year_start),
            ('date', '<=', today_dt)
        ])
        
        expenses_count = len(current_month_expenses)
        current_month_total = sum(current_month_expenses.mapped('total_amount'))
        ytd_total = sum(ytd_expenses.mapped('total_amount'))
        
        # Expense breakdown by status
        submitted_expenses = current_month_expenses.filtered(lambda x: x.sheet_id and x.sheet_id.state == 'submit')
        approved_expenses = current_month_expenses.filtered(lambda x: x.sheet_id and x.sheet_id.state == 'approve')
        draft_expenses = current_month_expenses.filtered(lambda x: not x.sheet_id or x.sheet_id.state == 'draft')
        
        expense_stats = {
            'total_count': expenses_count,
            'total_amount': current_month_total,
            'ytd_total': ytd_total,
            'submitted_count': len(submitted_expenses),
            'submitted_amount': sum(submitted_expenses.mapped('total_amount')),
            'approved_count': len(approved_expenses),
            'approved_amount': sum(approved_expenses.mapped('total_amount')),
            'draft_count': len(draft_expenses),
            'draft_amount': sum(draft_expenses.mapped('total_amount')),
            'pending_count': len(submitted_expenses),
        }
        
        # Recent activities (for enhanced dashboard)
        recent_activities = []
        
        # Add recent attendance - show the most recent attendance for the activity feed
        if today_attendances:
            # Get most recent attendance record
            most_recent = today_attendances[0] if len(today_attendances) > 0 else None
            
            if most_recent:
                recent_activities.append({
                    'type': 'attendance',
                    'title': 'Checked In' if not most_recent.check_out else 'Completed Work Day',
                    'description': f"At {most_recent.check_in.strftime('%I:%M %p')}" if not most_recent.check_out else f"Worked {most_recent.worked_hours:.2f} hours",
                    'time': most_recent.check_in,
                    'icon': 'clock-o',
                    'color': 'primary'
                })
        
        # Add recent CRM activities
        if crm_leads_count > 0:
            recent_activities.append({
                'type': 'crm',
                'title': 'CRM Active',
                'description': f"{crm_leads_count} leads to manage",
                'time': datetime.now(),
                'icon': 'briefcase',
                'color': 'info'
            })
        
        # Add recent expenses
        if current_month_expenses:
            recent_activities.append({
                'type': 'expense',
                'title': 'Expense Updates',
                'description': f"{len(current_month_expenses)} expenses this month",
                'time': datetime.now(),
                'icon': 'money',
                'color': 'warning'
            })
        
        # Sort activities by time
        recent_activities.sort(key=lambda x: x['time'], reverse=True)
        
        # Performance metrics (for enhanced dashboard)
        performance_metrics = {
            'attendance_rate': self._calculate_attendance_rate(employee, today_local),
            'crm_conversion_rate': (len(won_leads) / crm_leads_count * 100) if crm_leads_count > 0 else 0,
            'expense_avg_amount': current_month_total / expenses_count if expenses_count > 0 else 0,
            'weekly_hours': weekly_hours,
            'monthly_targets': self._get_monthly_targets(employee),
        }
        
        dashboard_data.update({
            'payslips_count': payslips_count,
            'latest_payslip': latest_payslip,
            'today_attendances': today_attendances,
            'weekly_hours': weekly_hours,
            'crm_leads_count': crm_leads_count,
            'crm_analytics': {
                'total_leads': crm_leads_count,
                'new_leads': len(new_leads),
                'won_leads': len(won_leads),
                'total_revenue': total_revenue,
                'conversion_rate': (len(won_leads) / crm_leads_count * 100) if crm_leads_count > 0 else 0
            },
            'expenses_count': expenses_count,
            'expense_stats': expense_stats,
            'recent_activities': recent_activities[:5],  # Top 5 recent activities
            'performance_metrics': performance_metrics,
        })
        
        return dashboard_data

    def _calculate_attendance_rate(self, employee, today_local):
        """Calculate monthly attendance rate using timezone-aware dates"""
        from datetime import datetime, timedelta
        import pytz
        
        # Get user's timezone
        user_timezone = get_user_timezone()
        user_pytz = pytz.timezone(user_timezone)
        
        # Get first day of current month in user's timezone
        first_day_local = today_local.replace(day=1)
        
        # Count working days (excluding weekends)
        working_days = 0
        current_date = first_day_local
        while current_date <= today_local:
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                working_days += 1
            current_date += timedelta(days=1)
        
        # Convert dates to datetime with timezone
        first_day_dt = datetime.combine(first_day_local, datetime.min.time()).replace(tzinfo=user_pytz)
        today_dt = datetime.combine(today_local, datetime.max.time()).replace(tzinfo=user_pytz)
        
        # Convert to UTC for database query
        utc_first_day = first_day_dt.astimezone(pytz.UTC)
        utc_today = today_dt.astimezone(pytz.UTC)
        
        # Count actual attendance days
        attendance_records = request.env[HR_ATTENDANCE_MODEL].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', utc_first_day),
            ('check_in', '<=', utc_today)
        ])
        
        # Get unique days using user's timezone for accurate day counting
        attended_days = set()
        for att in attendance_records:
            # Convert each check-in time to user's timezone to get the local date
            local_date = fields.Datetime.context_timestamp(request.env.user, att.check_in).date()
            attended_days.add(local_date)
        
        return (len(attended_days) / working_days * 100) if working_days > 0 else 0

    def _get_monthly_targets(self, employee):
        """Get monthly targets for the employee (placeholder)"""
        return {
            'attendance_target': 95,  # 95% attendance rate
            'crm_leads_target': 10,   # 10 leads per month
            'expense_budget': 2000,   # $2000 monthly expense budget
        }

    @http.route(MY_EMPLOYEE_URL + '/personal', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_personal(self, **post):
        employee = self._get_employee()
        if request.httprequest.method == 'POST':
            try:
                # Enhanced personal details update with validation
                vals = {}
                
                # Basic information
                if post.get('work_email'):
                    # Validate email format
                    import re
                    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                    if re.match(email_pattern, post.get('work_email')):
                        vals['work_email'] = post.get('work_email')
                    else:
                        return request.make_json_response({
                            'success': False,
                            'error': 'Invalid email format'
                        })
                
                if post.get('work_phone'):
                    vals['work_phone'] = post.get('work_phone')
                if post.get('birthday'):
                    vals['birthday'] = post.get('birthday')
                if post.get('gender'):
                    vals['gender'] = post.get('gender')
                if post.get('marital'):
                    vals['marital'] = post.get('marital')
                
                # Identity documents
                if post.get('x_nationality'):
                    vals['x_nationality'] = post.get('x_nationality')
                if post.get('x_emirates_id'):
                    vals['x_emirates_id'] = post.get('x_emirates_id')
                if post.get('x_emirates_expiry'):
                    vals['x_emirates_expiry'] = post.get('x_emirates_expiry')
                if post.get('x_passport_number'):
                    vals['x_passport_number'] = post.get('x_passport_number')
                if post.get('x_passport_country'):
                    vals['x_passport_country'] = post.get('x_passport_country')
                if post.get('x_passport_issue'):
                    vals['x_passport_issue'] = post.get('x_passport_issue')
                if post.get('x_passport_expiry'):
                    vals['x_passport_expiry'] = post.get('x_passport_expiry')
                
                # Contact information
                if post.get('private_email'):
                    vals['private_email'] = post.get('private_email')
                if post.get('private_phone'):
                    vals['private_phone'] = post.get('private_phone')
                if post.get('private_street'):
                    vals['private_street'] = post.get('private_street')
                if post.get('private_street2'):
                    vals['private_street2'] = post.get('private_street2')
                if post.get('private_city'):
                    vals['private_city'] = post.get('private_city')
                if post.get('private_zip'):
                    vals['private_zip'] = post.get('private_zip')
                
                # Emergency contact
                if post.get('emergency_contact'):
                    vals['emergency_contact'] = post.get('emergency_contact')
                if post.get('emergency_phone'):
                    vals['emergency_phone'] = post.get('emergency_phone')
                
                # Update employee record
                employee.sudo().write(vals)
                
                # Handle document uploads
                self._handle_document_uploads(employee, request.httprequest.files)
                
                return request.make_json_response({
                    'success': True,
                    'message': 'Personal details updated successfully'
                })
                
            except Exception as e:
                return request.make_json_response({
                    'success': False,
                    'error': str(e)
                })
        
        return request.render('employee_self_service_portal.portal_employee_profile_personal', {
            'employee': employee,
            'section': 'personal',
        })

    @http.route(MY_EMPLOYEE_URL + '/upload-photo', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_upload_photo(self, **post):
        """Handle employee photo upload"""
        try:
            employee = self._get_employee()
            
            # Get uploaded file
            photo_file = request.httprequest.files.get('photo')
            if not photo_file:
                return request.make_json_response({
                    'success': False,
                    'error': 'No photo file provided'
                })
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if photo_file.content_type not in allowed_types:
                return request.make_json_response({
                    'success': False,
                    'error': 'Invalid file type. Please upload JPG, PNG, or GIF only.'
                })
            
            # Validate file size (5MB max)
            max_size = 5 * 1024 * 1024  # 5MB
            photo_file.seek(0, 2)  # Seek to end
            file_size = photo_file.tell()
            photo_file.seek(0)  # Seek back to beginning
            
            if file_size > max_size:
                return request.make_json_response({
                    'success': False,
                    'error': 'File too large. Maximum size is 5MB.'
                })
            
            # Read and encode image
            import base64
            photo_data = base64.b64encode(photo_file.read())
            
            # Update employee image
            employee.sudo().write({
                'image_1920': photo_data
            })
            
            return request.make_json_response({
                'success': True,
                'message': 'Photo uploaded successfully',
                'image_url': f'/web/image/hr.employee/{employee.id}/image_1920/150x150'
            })
            
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': f'Upload failed: {str(e)}'
            })

    @http.route(MY_EMPLOYEE_URL + '/export-pdf', type='http', auth='user', website=True)
    def portal_employee_export_pdf(self, **kwargs):
        """Export employee profile as PDF"""
        try:
            employee = self._get_employee()
            
            # Create PDF using reportlab or return HTML for now
            html_content = request.env['ir.qweb']._render('employee_self_service_portal.profile_pdf_template', {
                'employee': employee,
                'company': request.env.company,
            })
            
            # Convert HTML to PDF (simplified version)
            pdf_data = html_content.encode('utf-8')
            
            return request.make_response(
                pdf_data,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', f'attachment; filename="profile_{employee.name.replace(" ", "_")}.pdf"')
                ]
            )
            
        except Exception as e:
            return request.redirect('/my/employee/personal?error=export_failed')

    def _handle_document_uploads(self, employee, files):
        """Handle document file uploads"""
        try:
            import base64
            
            # Handle Emirates ID file
            emirates_file = files.get('emirates_id_file')
            if emirates_file and emirates_file.filename:
                self._save_employee_document(employee, emirates_file, 'Emirates ID')
            
            # Handle Passport file
            passport_file = files.get('passport_file')
            if passport_file and passport_file.filename:
                self._save_employee_document(employee, passport_file, 'Passport')
            
            # Handle other documents
            other_files = files.getlist('other_documents')
            for file in other_files:
                if file and file.filename:
                    self._save_employee_document(employee, file, 'Other Document')
                    
        except Exception as e:
            _logger.error(f"Error handling document uploads: {str(e)}")

    def _save_employee_document(self, employee, file, doc_type):
        """Save individual document file"""
        try:
            import base64
            
            # Validate file size (10MB max)
            max_size = 10 * 1024 * 1024
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > max_size:
                return
            
            # Read file data
            file_data = base64.b64encode(file.read())
            
            # Create attachment
            attachment = request.env['ir.attachment'].sudo().create({
                'name': f"{doc_type} - {file.filename}",
                'datas': file_data,
                'res_model': 'hr.employee',
                'res_id': employee.id,
                'public': False,
                'type': 'binary',
            })
            
            return attachment
            
        except Exception as e:
            _logger.error(f"Error saving document {file.filename}: {str(e)}")
            return None

    @http.route(MY_EMPLOYEE_URL + '/experience', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_experience(self, **post):
        employee = self._get_employee()
        if request.httprequest.method == 'POST':
            try:
                vals = {}
                
                # Validate and update experience
                experience = post.get('x_experience', '').strip()
                if experience:
                    # Basic validation - minimum word count
                    word_count = len(experience.split())
                    if word_count < 10:
                        return request.make_json_response({
                            'success': False,
                            'error': 'Experience description should be at least 10 words.'
                        })
                    vals['x_experience'] = experience
                
                # Validate and update skills
                skills = post.get('x_skills', '').strip()
                if skills:
                    # Clean up skills - remove extra spaces and normalize
                    skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
                    if len(skills_list) < 3:
                        return request.make_json_response({
                            'success': False,
                            'error': 'Please add at least 3 skills.'
                        })
                    vals['x_skills'] = ', '.join(skills_list)
                
                # Experience field is already handled above
                
                # Update employee record
                employee.sudo().write(vals)
                
                # Handle document uploads for experience section
                self._handle_experience_documents(employee, request.httprequest.files)
                
                return request.make_json_response({
                    'success': True,
                    'message': 'Experience and skills updated successfully'
                })
                
            except Exception as e:
                return request.make_json_response({
                    'success': False,
                    'error': str(e)
                })
        
        return request.render('employee_self_service_portal.portal_employee_profile_experience', {
            'employee': employee,
            'section': 'experience',
        })

    def _handle_experience_documents(self, employee, files):
        """Handle experience-related document uploads"""
        try:
            # Handle Resume/CV
            resume_file = files.get('resume_file')
            if resume_file and resume_file.filename:
                self._save_employee_document(employee, resume_file, 'Resume/CV')
            
            # Handle Training Certificates
            training_files = files.getlist('training_certificates')
            for file in training_files:
                if file and file.filename:
                    self._save_employee_document(employee, file, 'Training Certificate')
            
            # Handle Awards
            award_files = files.getlist('awards_files')
            for file in award_files:
                if file and file.filename:
                    self._save_employee_document(employee, file, 'Award/Recognition')
                    
        except Exception as e:
            _logger.error(f"Error handling experience documents: {str(e)}")

    @http.route(MY_EMPLOYEE_URL + '/certification', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_certification(self, **post):
        employee = self._get_employee()
        if request.httprequest.method == 'POST':
            vals = {
                'x_certifications': post.get('x_certifications'),
            }
            employee.sudo().write({k: v for k, v in vals.items() if v is not None})
        return request.render('employee_self_service_portal.portal_employee_profile_certification', {
            'employee': employee,
            'section': 'certification',
        })

    @http.route(MY_EMPLOYEE_URL + '/bank', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_bank(self, **post):
        employee = self._get_employee()
        if request.httprequest.method == 'POST':
            vals = {
                'x_bank_account': post.get('x_bank_account'),
                'x_bank_name': post.get('x_bank_name'),
                'x_ifsc': post.get('x_ifsc'),
            }
            employee.sudo().write({k: v for k, v in vals.items() if v is not None})
        return request.render('employee_self_service_portal.portal_employee_profile_bank', {
            'employee': employee,
            'section': 'bank',
        })

    @http.route('/my/employee/crm', type='http', auth='user', website=True)
    @check_portal_access('crm')
    def portal_employee_crm(self, **kwargs):
        employee = self._get_employee()
        user = request.env.user
        
        # Build base domain
        domain = [('user_id', '=', user.id)]
        
        # Apply filters based on parameters
        stage_filter = kwargs.get('stage')
        if stage_filter:
            domain.append(('stage_id', '=', int(stage_filter)))
            
        practice_filter = kwargs.get('practice')
        if practice_filter:
            # Only apply practice filter if the field exists on the model
            lead_model = request.env['crm.lead']
            if 'practice_id' in lead_model._fields:
                domain.append(('practice_id', '=', int(practice_filter)))
            
        industry_filter = kwargs.get('industry')
        if industry_filter:
            # Only apply industry filter if the field exists on the model
            lead_model = request.env['crm.lead']
            if 'industry_id' in lead_model._fields:
                domain.append(('industry_id', '=', int(industry_filter)))
            
        priority_filter = kwargs.get('priority')
        if priority_filter:
            domain.append(('priority', '=', priority_filter))
            
        # Date range filters
        date_from = kwargs.get('date_from')
        if date_from:
            domain.append(('create_date', '>=', date_from + ' 00:00:00'))
            
        date_to = kwargs.get('date_to')
        if date_to:
            domain.append(('create_date', '<=', date_to + ' 23:59:59'))
            
        # Activity due date filters - filter through activity_ids
        activity_due_from = kwargs.get('activity_due_from')
        if activity_due_from:
            domain.append(('activity_ids.date_deadline', '>=', activity_due_from))
            
        activity_due_to = kwargs.get('activity_due_to')
        if activity_due_to:
            domain.append(('activity_ids.date_deadline', '<=', activity_due_to))
            
        # Quick activity filters
        quick_activity = kwargs.get('quick_activity')
        if quick_activity:
            from datetime import date, timedelta
            today = date.today()
            
            if quick_activity == 'today':
                domain.append(('activity_ids.date_deadline', '=', today))
            elif quick_activity == 'yesterday':
                yesterday = today - timedelta(days=1)
                domain.append(('activity_ids.date_deadline', '=', yesterday))
            elif quick_activity == 'tomorrow':
                tomorrow = today + timedelta(days=1)
                domain.append(('activity_ids.date_deadline', '=', tomorrow))
            elif quick_activity == 'past':
                domain.append(('activity_ids.date_deadline', '<', today))
            elif quick_activity == 'future':
                domain.append(('activity_ids.date_deadline', '>', today))
            elif quick_activity == 'this_week':
                # Monday of current week
                monday = today - timedelta(days=today.weekday())
                sunday = monday + timedelta(days=6)
                domain.append(('activity_ids.date_deadline', '>=', monday))
                domain.append(('activity_ids.date_deadline', '<=', sunday))
            elif quick_activity == 'overdue':
                domain.append(('activity_ids.date_deadline', '<', today))
            elif quick_activity == 'no_activities':
                domain.append(('activity_ids', '=', False))
        
        # Tags filter
        tags_filter = kwargs.get('tags')
        if tags_filter:
            try:
                # Handle both single tag and multiple tags
                if isinstance(tags_filter, str):
                    tag_ids = [int(tags_filter)]
                else:
                    tag_ids = [int(tag) for tag in tags_filter if tag]
                
                if tag_ids:
                    # Check if tag_ids field exists
                    lead_model = request.env['crm.lead']
                    if 'tag_ids' in lead_model._fields:
                        domain.append(('tag_ids', 'in', tag_ids))
            except (ValueError, TypeError):
                pass  # Skip invalid tag values
        
        leads = request.env['crm.lead'].sudo().search(domain, order='priority desc, create_date desc')
        
        # Custom sorting by nearest activity date
        def get_next_activity_date(lead):
            """Get the nearest activity date for sorting"""
            if not lead.activity_ids:
                return date.max  # Leads without activities go to the end
            
            next_activity = lead.activity_ids.sorted('date_deadline')
            if next_activity and next_activity[0].date_deadline:
                activity_date = next_activity[0].date_deadline
                # Convert datetime to date if needed
                if hasattr(activity_date, 'date'):
                    return activity_date.date()
                return activity_date
            return date.max
        
        # Sort leads by nearest activity date, then by priority, then by create date
        from datetime import date
        leads = leads.sorted(key=lambda lead: (
            get_next_activity_date(lead),  # Nearest activity first
            -int(lead.priority or '0'),    # Higher priority first (reversed)
            -lead.id                       # Newer leads first (reversed by ID)
        ))
        
        # Get filter options for dropdowns - show ALL available options, not just used ones
        all_user_leads = request.env['crm.lead'].sudo().search([('user_id', '=', user.id)])
        
        # Get ALL stages available in the system
        stages = request.env['crm.stage'].sudo().search([], order='sequence, name')
        
        # Handle practices safely - check if model and field exist
        practices = []
        try:
            if 'practice_id' in all_user_leads._fields:
                # Try different possible model names for practice and get ALL practices
                practice_model = None
                for model_name in ['x_practice', 'crm.practice', 'practice', 'x_crm_practice']:
                    try:
                        practice_model = request.env[model_name]
                        break
                    except KeyError:
                        continue
                
                if practice_model:
                    practices = practice_model.sudo().search([], order='name')
        except Exception:
            practices = []
            
        industries = []
        try:
            if 'industry_id' in all_user_leads._fields:
                # Get ALL industries available in the system
                industries = request.env['res.partner.industry'].sudo().search([], order='name')
        except Exception:
            industries = []
            
        # Get tags for filter options - show ALL available tags
        tags = []
        try:
            if 'tag_ids' in all_user_leads._fields:
                # Get ALL tags available in the system
                tags = request.env['crm.tag'].sudo().search([], order='name')
        except Exception:
            tags = []
        
        # Process leads to add computed fields for template
        import datetime
        import re
        from odoo import fields
        
        today = datetime.date.today()
        processed_leads = []
        
        for lead in leads:
            lead_data = {
                'record': lead,
                'activity_summary': self._get_activity_summary(lead),
                'next_activity_info': self._get_next_activity_info(lead, today),
                'recent_note_info': self._get_recent_note_info(lead),
            }
            processed_leads.append(lead_data)
        
        # Check if enhanced view is requested
        view_type = kwargs.get('view', 'list')  # Default to list view instead of enhanced view
        template_name = 'employee_self_service_portal.portal_employee_crm_enhanced' if view_type == 'enhanced' else 'employee_self_service_portal.portal_employee_crm'
        
        # Calculate dashboard KPIs for enhanced view
        dashboard_kpis = {}
        if view_type == 'enhanced':
            all_user_leads_current = request.env['crm.lead'].sudo().search([('user_id', '=', user.id)])
            dashboard_kpis = self._calculate_dashboard_kpis(all_user_leads_current, today)
        
        return request.render(template_name, {
            'employee': employee,
            'leads': leads,  # Keep original for compatibility
            'processed_leads': processed_leads,
            'stages': stages,  # Add stages for dropdown
            'filter_stages': stages,  # Filter options
            'filter_practices': practices,
            'filter_industries': industries,
            'filter_tags': tags,
            'dashboard_kpis': dashboard_kpis,  # For enhanced view
            'view_type': view_type,  # Current view type
            # Current filter values for maintaining state
            'current_filters': {
                'stage': stage_filter or '',
                'practice': practice_filter or '',
                'industry': industry_filter or '',
                'priority': priority_filter or '',
                'date_from': date_from or '',
                'date_to': date_to or '',
                'activity_due_from': activity_due_from or '',
                'activity_due_to': activity_due_to or '',
                'quick_activity': quick_activity or '',
                'tags': tags_filter or '',
                'view': view_type,
            }
        })
    
    def _get_activity_summary(self, lead):
        """Get activity summary for a lead"""
        activity_count = len(lead.activity_ids)
        return {
            'count': activity_count,
            'has_activities': activity_count > 0
        }
    
    def _get_next_activity_info(self, lead, today):
        """Get next activity information with relative date"""
        if not lead.activity_ids:
            return {'has_activity': False}
        
        next_activity = lead.activity_ids.sorted('date_deadline')[0]
        activity_date = next_activity.date_deadline
        
        if not activity_date:
            return {
                'has_activity': True,
                'activity_type': next_activity.activity_type_id.name,
                'user_name': next_activity.user_id.name,
                'relative_date': 'No date',
                'badge_class': 'badge-secondary'
            }
        
        # Convert to date if it's datetime
        if hasattr(activity_date, 'date'):
            activity_date = activity_date.date()
        
        date_diff = (activity_date - today).days
        
        # Determine relative date text and badge class
        if date_diff == 0:
            relative_date = 'Today'
            badge_class = 'badge-warning'
        elif date_diff == 1:
            relative_date = 'Tomorrow'
            badge_class = 'badge-info'
        elif date_diff == -1:
            relative_date = 'Yesterday'
            badge_class = 'badge-danger'
        elif date_diff < 0:
            relative_date = f'Overdue {abs(date_diff)} days'
            badge_class = 'badge-danger'
        else:
            relative_date = f'Due in {date_diff} days'
            badge_class = 'badge-info'
        
        return {
            'has_activity': True,
            'activity_type': next_activity.activity_type_id.name,
            'user_name': next_activity.user_id.name,
            'relative_date': relative_date,
            'badge_class': badge_class
        }
    
    def _get_recent_note_info(self, lead):
        """Get recent note information"""
        import re
        
        recent_notes = lead.message_ids.filtered(
            lambda m: m.message_type == 'comment' and m.body and m.body.strip()
        )
        
        if not recent_notes:
            return {'has_note': False}
        
        recent_note = recent_notes[0]
        
        # Clean HTML tags from body
        clean_body = re.sub(r'<[^>]+>', '', recent_note.body or '').strip()
        
        # Truncate if too long
        if len(clean_body) > 47:
            clean_body = clean_body[:47] + '...'
        
        # Format date
        date_str = ''
        if recent_note.date:
            date_str = recent_note.date.strftime('%m/%d %H:%M')
        
        return {
            'has_note': True,
            'author_name': recent_note.author_id.name or 'System',
            'date_str': date_str,
            'clean_body': clean_body,
            'full_body': recent_note.body or ''
        }

    def _calculate_dashboard_kpis(self, leads, today):
        """Calculate KPIs for the enhanced CRM dashboard"""
        from datetime import timedelta
        
        total_leads = len(leads)
        
        # Count leads by stage
        new_leads = leads.filtered(lambda l: l.stage_id.name in ['New', 'Qualification'] if l.stage_id else False)
        in_progress_leads = leads.filtered(lambda l: l.stage_id.name in ['Qualified', 'Proposition'] if l.stage_id else False)
        won_leads = leads.filtered(lambda l: l.stage_id.name == 'Won' if l.stage_id else False)
        
        # Calculate revenue
        total_revenue = sum(leads.mapped('expected_revenue'))
        won_revenue = sum(won_leads.mapped('expected_revenue'))
        
        # Activity metrics
        overdue_activities = 0
        today_activities = 0
        
        for lead in leads:
            for activity in lead.activity_ids:
                if activity.date_deadline:
                    activity_date = activity.date_deadline
                    if hasattr(activity_date, 'date'):
                        activity_date = activity_date.date()
                    
                    if activity_date < today:
                        overdue_activities += 1
                    elif activity_date == today:
                        today_activities += 1
        
        # Conversion rate (won leads / total leads)
        conversion_rate = (len(won_leads) / total_leads * 100) if total_leads > 0 else 0
        
        return {
            'total_leads': total_leads,
            'new_leads': len(new_leads),
            'in_progress_leads': len(in_progress_leads),
            'won_leads': len(won_leads),
            'total_revenue': total_revenue,
            'won_revenue': won_revenue,
            'overdue_activities': overdue_activities,
            'today_activities': today_activities,
            'conversion_rate': round(conversion_rate, 1),
        }

    @http.route('/my/employee/crm/create', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_crm_create(self, **post):
        user = request.env.user
        if request.httprequest.method == 'POST':
            # Process partner_id (customer) - handle creation of new customers
            partner_id = _process_partner_field(post.get('partner_id'), 'partner_id')
            
            # Process point_of_contact_id - handle creation of new contacts
            point_of_contact_id = _process_partner_field(post.get('point_of_contact_id'), 'point_of_contact_id')
            
            vals = {
                'name': post.get('name'),
                'partner_id': partner_id,
                'email_from': post.get('email_from'),
                'phone': post.get('phone'),
                'expected_revenue': post.get('expected_revenue') or 0.0,
                'user_id': user.id,
                'stage_id': post.get('stage_id') or False,
                'description': post.get('description'),
                'probability': post.get('probability') or 0.0,
                'date_deadline': post.get('date_deadline') or False,
                # TechCarrot CRM MLR custom fields
                'point_of_contact_id': point_of_contact_id,
                'practice_id': post.get('practice_id') or False,
                'deal_manager_id': post.get('deal_manager_id') or False,
                'client_proposal_submission_date': post.get('client_proposal_submission_date') or False,
                'proposal_submitted_date': post.get('proposal_submitted_date') or False,
                'engaged_presales': bool(post.get('engaged_presales')),
                'industry_id': post.get('industry_id') or False,
                'type_id': post.get('type_id') or False,
            }
            lead = request.env['crm.lead'].sudo().create(vals)
            tag_id_list = _process_tag_ids(post)
            # Always update tag_ids, even if empty (to allow clearing all tags)
            lead.sudo().write({'tag_ids': [(6, 0, tag_id_list)]})
            return request.redirect(CRM_REDIRECT_URL)
        partners = request.env['res.partner'].sudo().search([])
        # Get contacts for point of contact field
        contacts = request.env['res.partner'].sudo().search([('is_company', '=', False)])
        stages = request.env['crm.stage'].sudo().search([])
        all_tags = request.env[CRM_TAG_MODEL].sudo().search([])
        # Show all users (internal and portal) as salespersons
        salespersons = request.env['res.users'].sudo().search([('active', '=', True)])
        # Get TechCarrot CRM MLR related data
        practices = request.env['crm.practice'].sudo().search([('active', '=', True)])
        industries = request.env['crm.industry'].sudo().search([('active', '=', True)])
        lead_types = request.env['crm.lead.type'].sudo().search([('active', '=', True)])
        employees = request.env['hr.employee'].sudo().search([('active', '=', True)])
        current_user_id = request.env.user.id
        return request.render('employee_self_service_portal.portal_employee_crm_create', {
            'partners': partners,
            'contacts': contacts,
            'stages': stages,
            'all_tags': all_tags,
            'salespersons': salespersons,
            'practices': practices,
            'industries': industries,
            'lead_types': lead_types,
            'employees': employees,
            'current_user_id': current_user_id,
        })

    @http.route('/my/employee/crm/edit/<int:lead_id>', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_crm_edit(self, lead_id, **post):
        lead = request.env[CRM_LEAD_MODEL].sudo().browse(lead_id)
        user = request.env.user
        if not lead or lead.user_id.id != user.id:
            return request.redirect(CRM_REDIRECT_URL)
        if request.httprequest.method == 'POST':
            # Process point_of_contact_id - handle creation of new contacts
            point_of_contact_id = _process_partner_field(post.get('point_of_contact_id'), 'point_of_contact_id')
            
            vals = {
                'name': post.get('name'),
                'email_from': post.get('email_from'),
                'phone': post.get('phone'),
                'description': post.get('description'),
                'date_deadline': post.get('date_deadline'),
                # TechCarrot CRM MLR custom fields
                'point_of_contact_id': point_of_contact_id,
                'practice_id': post.get('practice_id') or False,
                'deal_manager_id': post.get('deal_manager_id') or False,
                'client_proposal_submission_date': post.get('client_proposal_submission_date') or False,
                'proposal_submitted_date': post.get('proposal_submitted_date') or False,
                'engaged_presales': bool(post.get('engaged_presales')),
                'industry_id': post.get('industry_id') or False,
                'type_id': post.get('type_id') or False,
            }
            # Convert probability and expected_revenue to float if present
            prob = post.get('probability')
            if prob:
                try:
                    vals['probability'] = float(prob)
                except Exception:
                    pass
            exp_rev = post.get('expected_revenue')
            if exp_rev:
                try:
                    vals['expected_revenue'] = float(exp_rev)
                except Exception:
                    pass
            # Validate stage_id
            stage_id = post.get('stage_id')
            if stage_id:
                try:
                    stage_id_int = int(stage_id)
                    stage = request.env[CRM_STAGE_MODEL].sudo().browse(stage_id_int)
                    if stage.exists():
                        vals['stage_id'] = stage_id_int
                except Exception:
                    pass
            lead.sudo().write({k: v for k, v in vals.items() if v is not None})
            tag_id_list = _process_tag_ids(post)
            lead.sudo().write({'tag_ids': [(6, 0, tag_id_list)]})
            return request.redirect(CRM_REDIRECT_URL)
        stages = request.env[CRM_STAGE_MODEL].sudo().search([])
        partners = request.env['res.partner'].sudo().search([])
        # Get contacts for point of contact field
        contacts = request.env['res.partner'].sudo().search([('is_company', '=', False)])
        all_tags = request.env[CRM_TAG_MODEL].sudo().search([])
        salespersons = request.env['res.users'].sudo().search([('active', '=', True)])
        # Get TechCarrot CRM MLR related data
        practices = request.env['crm.practice'].sudo().search([('active', '=', True)])
        industries = request.env['crm.industry'].sudo().search([('active', '=', True)])
        lead_types = request.env['crm.lead.type'].sudo().search([('active', '=', True)])
        employees = request.env['hr.employee'].sudo().search([('active', '=', True)])
        activity_types = request.env['mail.activity.type'].sudo().search([])
        default_activity_type_id = request.env.ref('mail.mail_activity_data_todo').id if request.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False) else (activity_types and activity_types[0].id or False)
        return request.render('employee_self_service_portal.portal_employee_crm_edit', {
            'lead': lead,
            'stages': stages,
            'all_tags': all_tags,
            'partners': partners,
            'contacts': contacts,
            'salespersons': salespersons,
            'practices': practices,
            'industries': industries,
            'lead_types': lead_types,
            'employees': employees,
            'activity_types': activity_types,
            'default_activity_type_id': default_activity_type_id,
        })

    @http.route('/my/employee/crm/delete/<int:lead_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_crm_delete(self, lead_id, **post):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        if lead and lead.user_id.id == user.id:
            lead.sudo().unlink()
        return request.redirect('/my/employee/crm')

    @http.route('/my/employee/crm/log_note/<int:lead_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_crm_log_note(self, lead_id, **post):
        import logging
        _logger = logging.getLogger(__name__)
        lead = request.env[CRM_LEAD_MODEL].sudo().browse(lead_id)
        user = request.env.user
        note = post.get('note')
        file_keys = list(request.httprequest.files.keys())
        _logger.info('ESS Portal: Received file keys: %s', file_keys)
        files = []
        if hasattr(request.httprequest.files, 'getlist'):
            files = request.httprequest.files.getlist('attachments')
        elif 'attachments' in request.httprequest.files:
            file = request.httprequest.files['attachments']
            if file:
                files = [file]
        _logger.info('ESS Portal: Number of files in attachments: %s', len(files))
        for f in files:
            _logger.info('ESS Portal: File received: filename=%s content_type=%s', getattr(f, 'filename', None), getattr(f, 'content_type', None))
        # Allow log note with or without text, as long as there are files or a note
        if lead and (note or files) and lead.user_id.id == user.id:
            msg = lead.message_post(body=note or '', message_type='comment', author_id=user.partner_id.id)
            import base64
            attachment_ids = []
            for file in files:
                try:
                    file.seek(0)
                except Exception:
                    pass
                file_content = file.read()
                if file_content:
                    if isinstance(file_content, str):
                        file_content = file_content.encode('utf-8')
                    encoded_content = base64.b64encode(file_content).decode('utf-8')
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': file.filename,
                        'datas': encoded_content,
                        'res_model': 'crm.lead',
                        'res_id': lead.id,
                        'mimetype': file.mimetype,
                        'type': 'binary',
                        'public': True,
                    })
                    attachment_ids.append(attachment.id)
                    _logger.info('ESS Portal: Created attachment id=%s name=%s res_model=%s res_id=%s', attachment.id, attachment.name, attachment.res_model, attachment.res_id)
            if attachment_ids:
                msg.sudo().write({'attachment_ids': [(4, att_id) for att_id in attachment_ids]})
        return request.redirect(f'/my/employee/crm/edit/{lead_id}')

    @http.route('/my/employee/crm/add_activity/<int:lead_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_crm_add_activity(self, lead_id, **post):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        summary = post.get('summary')
        date_deadline = post.get('date_deadline')
        note = post.get('note')
        activity_type_id = post.get('activity_type_id')
        assigned_user_id = post.get('assigned_user_id')
        if lead and summary and date_deadline and lead.user_id.id == user.id:
            activity_type_xmlid = None
            activity_type_name = ''
            if activity_type_id:
                activity_type = request.env['mail.activity.type'].sudo().browse(int(activity_type_id))
                external_ids = activity_type.get_external_id()
                activity_type_xmlid = external_ids.get(activity_type.id)
                activity_type_name = activity_type.name
            if not activity_type_xmlid:
                activity_type_xmlid = 'mail.mail_activity_data_todo'
                activity_type_name = 'To Do'
            assigned_uid = int(assigned_user_id) if assigned_user_id else user.id
            assigned_user = request.env['res.users'].sudo().browse(assigned_uid)
            lead.activity_schedule(
                activity_type_xmlid,
                summary=summary,
                note=note,
                date_deadline=date_deadline,
                user_id=assigned_uid
            )
            # Log in chatter, escape note
            msg = f"Activity created: <b>{activity_type_name}</b> - <b>{summary}</b> (Assigned to: {assigned_user.name}, Due: {date_deadline})"
            if note:
                msg += f"<br/>Note: {html.escape(note)}"
            lead.message_post(body=msg)
        
        # Check if request came from modal (via referer or special parameter)
        referer = request.httprequest.environ.get('HTTP_REFERER', '')
        if 'activity_modal' in referer or post.get('from_modal'):
            return request.redirect('/my/employee/crm')
        else:
            return request.redirect(f'/my/employee/crm/edit/{lead_id}')

    @http.route('/my/employee/crm/activity_done/<int:activity_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_crm_activity_done(self, activity_id, **post):
        activity = request.env['mail.activity'].sudo().browse(activity_id)
        lead_id = int(request.params.get('lead_id', 0))
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        # Security: Only allow if user owns the lead
        if activity and lead and lead.user_id.id == user.id and activity.res_model == 'crm.lead' and activity.res_id == lead.id:
            try:
                activity.action_done()
            except Exception:
                pass
        
        # Check if request came from modal
        referer = request.httprequest.environ.get('HTTP_REFERER', '')
        if 'activity_modal' in referer or post.get('from_modal'):
            return request.redirect('/my/employee/crm')
        else:
            return request.redirect(f'/my/employee/crm/edit/{lead_id}')

    @http.route('/my/employee/crm/activity_edit/<int:activity_id>', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_crm_activity_edit(self, activity_id, **post):
        activity = request.env['mail.activity'].sudo().browse(activity_id)
        lead_id = int(request.params.get('lead_id', 0))
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        if not (activity and lead and lead.user_id.id == user.id and activity.res_model == 'crm.lead' and activity.res_id == lead.id):
            return request.redirect(f'/my/employee/crm/edit/{lead_id}')
        if request.httprequest.method == 'POST':
            vals = {}
            if post.get('summary') is not None:
                vals['summary'] = post.get('summary')
            if post.get('date_deadline') is not None:
                vals['date_deadline'] = post.get('date_deadline')
            if post.get('note') is not None:
                vals['note'] = post.get('note')
            if post.get('activity_type_id'):
                vals['activity_type_id'] = int(post.get('activity_type_id'))
            if post.get('user_id'):
                vals['user_id'] = int(post.get('user_id'))
            if vals:
                activity.sudo().write(vals)
                # Log in chatter, escape note
                activity_type_name = activity.activity_type_id.name or ''
                assigned_user = activity.user_id
                msg = f"Activity updated: <b>{activity_type_name}</b> - <b>{activity.summary}</b> (Assigned to: {assigned_user.name}, Due: {activity.date_deadline})"
                if activity.note:
                    msg += f"<br/>Note: {html.escape(activity.note)}"
                lead.message_post(body=msg)
            return request.redirect(f'/my/employee/crm/edit/{lead_id}')
        # GET: render a simple edit form (reuse activity_types and salespersons from lead edit)
        activity_types = request.env['mail.activity.type'].sudo().search([])
        salespersons = request.env['res.users'].sudo().search([('active', '=', True)])
        return request.render('employee_self_service_portal.portal_employee_crm_activity_edit', {
            'activity': activity,
            'lead': lead,
            'activity_types': activity_types,
            'salespersons': salespersons,
        })

    @http.route('/my/employee/crm/activity_delete/<int:activity_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_employee_crm_activity_delete(self, activity_id, **post):
        activity = request.env['mail.activity'].sudo().browse(activity_id)
        lead_id = int(request.params.get('lead_id', 0))
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        if activity and lead and lead.user_id.id == user.id and activity.res_model == 'crm.lead' and activity.res_id == lead.id:
            try:
                activity_type_name = activity.activity_type_id.name or ''
                summary = activity.summary or ''
                assigned_user = activity.user_id
                due = activity.date_deadline or ''
                note = activity.note or ''
                msg = f"Activity deleted: <b>{activity_type_name}</b> - <b>{summary}</b> (Assigned to: {assigned_user.name}, Due: {due})"
                if note:
                    msg += f"<br/>Note: {html.escape(note)}"
                activity.sudo().unlink()
                lead.message_post(body=msg)
            except Exception:
                pass
        
        # Check if request came from modal
        referer = request.httprequest.environ.get('HTTP_REFERER', '')
        if 'activity_modal' in referer or post.get('from_modal'):
            return request.redirect('/my/employee/crm')
        else:
            return request.redirect(f'/my/employee/crm/edit/{lead_id}')

    @http.route('/my/employee/crm/activity_modal/<int:lead_id>/<string:action>', type='http', auth='user', website=True)
    def portal_employee_crm_activity_modal(self, lead_id, action, **kwargs):
        """Route to handle activity modal content loading"""
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        
        # Security check - only allow access to own leads
        if not lead or lead.user_id.id != user.id:
            return '<div class="alert alert-danger">Access denied</div>'
        
        # Common data for both views
        activity_types = request.env['mail.activity.type'].sudo().search([])
        default_activity_type_id = request.env.ref('mail.mail_activity_data_todo').id if request.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False) else (activity_types and activity_types[0].id or False)
        salespersons = request.env['res.users'].sudo().search([('active', '=', True)])
        
        # Get today's date for comparison
        from datetime import date
        today = date.today()
        
        context = {
            'lead': lead,
            'activity_types': activity_types,
            'default_activity_type_id': default_activity_type_id,
            'salespersons': salespersons,
            'today': today,
        }
        
        if action == 'view':
            return request.render('employee_self_service_portal.portal_employee_crm_activity_modal_view', context)
        elif action == 'add':
            return request.render('employee_self_service_portal.portal_employee_crm_activity_modal_add', context)
        else:
            return '<div class="alert alert-danger">Invalid action</div>'

    @http.route(MY_EMPLOYEE_URL + '/expenses', type='http', auth='user', website=True)
    @check_portal_access('expenses')
    def portal_expense_history(self, **kwargs):
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        company_id = employee.company_id.id
        domain = [('employee_id', '=', employee.id)]
        # Filtering logic
        status = kwargs.get('status')
        if status:
            if status == 'withdrawn' or status == 'cancel':
                domain += [('sheet_id.state', '=', 'cancel')]
            else:
                domain += [('sheet_id.state', '=', status)]
        category = kwargs.get('category')
        if category:
            domain += [('product_id', '=', int(category))]
        date = kwargs.get('date')
        if date:
            domain += [('date', '=', date)]
        expenses = request.env['hr.expense'].sudo().search(domain, order='date desc')
        
        # Filter categories by the employee's company
        categories = request.env['product.product'].sudo().search([
            ('can_be_expensed', '=', True),
            '|',
            ('company_id', '=', False),
            ('company_id', '=', company_id)
        ])
        
        # Ensure we have access to the company currency
        company_currency = employee.company_id.currency_id
        
        return request.render('employee_self_service_portal.portal_expense', {
            'expenses': expenses,
            'employee': employee,
            'categories': categories,
            'selected_status': status or '',
            'selected_category': category or '',  # Pass as string
            'selected_date': date or '',
            'company_currency': company_currency,
        })

    @http.route(MY_EMPLOYEE_URL + '/expenses/submit', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_expense_submit(self, **post):
        import logging
        import base64
        _logger = logging.getLogger(__name__)
        
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        company_id = employee.company_id.id
        
        # Use product_id as category (many2one to product.product, can_be_expensed=True)
        # Filter by employee's company
        categories = request.env['product.product'].sudo().search([
            ('can_be_expensed', '=', True),
            '|',
            ('company_id', '=', False),
            ('company_id', '=', company_id)
        ])
        errors = []
        success = None
        
        if request.httprequest.method == 'POST':
            # Enhanced validation
            validation_errors = self._validate_expense_data(post)
            if validation_errors:
                errors.extend(validation_errors)
            else:
                try:
                    # Create expense record
                    vals = {
                        'name': post.get('name'),
                        'date': post.get('date'),
                        'employee_id': employee.id,
                        'total_amount': float(post.get('total_amount')),
                        'product_id': int(post.get('category_id')),
                        'description': post.get('notes', ''),
                        'company_id': company_id,  # Set the company_id to employee's company
                        'currency_id': employee.company_id.currency_id.id,  # Set currency based on employee's company
                    }
                    expense = request.env['hr.expense'].sudo().create(vals)
                    _logger.info("Created expense record with ID: %d", expense.id)
                    
                    # Handle file attachment
                    attachment = request.httprequest.files.get('attachment')
                    if attachment and attachment.filename:
                        try:
                            attachment_vals = {
                                'name': attachment.filename,
                                'datas': base64.b64encode(attachment.read()),
                                'res_model': 'hr.expense',
                                'res_id': expense.id,
                                'mimetype': attachment.content_type or 'application/octet-stream',
                                'description': 'Expense Receipt',
                            }
                            attachment_record = request.env['ir.attachment'].sudo().create(attachment_vals)
                            _logger.info("Created attachment with ID: %d for expense: %d", attachment_record.id, expense.id)
                        except Exception as attachment_error:
                            _logger.warning("Failed to save attachment: %s", str(attachment_error))
                            errors.append("Attachment could not be saved, but expense was created successfully.")
                    
                    # Find or create expense sheet and add expense
                    sheet = self._get_or_create_expense_sheet(employee, expense)
                    
                    success = 'Expense submitted successfully with receipt.' if attachment else 'Expense submitted successfully.'
                    _logger.info("Expense submission completed successfully")
                    
                except Exception as e:
                    _logger.error("Error creating expense: %s", str(e))
                    errors.append('Error submitting expense: %s' % str(e))
        
        # Ensure we have access to the company currency
        company_currency = employee.company_id.currency_id
        
        return request.render('employee_self_service_portal.portal_expense_submit', {
            'employee': employee,
            'categories': categories,
            'errors': errors if errors else None,
            'success': success,
            'company_currency': company_currency,
        })
    
    def _validate_expense_data(self, post):
        """Validate expense submission data"""
        import logging
        _logger = logging.getLogger(__name__)
        errors = []
        
        # Get employee for company-specific validations
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        currency_symbol = employee.company_id.currency_id.symbol or '$'
        
        # Required field validation
        required_fields = {
            'name': 'Description',
            'date': 'Date', 
            'total_amount': 'Amount',
            'category_id': 'Category'
        }
        
        for field, label in required_fields.items():
            if not post.get(field):
                errors.append(f'{label} is required.')
        
        # Amount validation
        try:
            amount = float(post.get('total_amount', 0))
            if amount <= 0:
                errors.append('Amount must be greater than 0.')
            elif amount > 50000:  # Business rule: max expense limit
                errors.append(f'Amount cannot exceed {currency_symbol}50,000.')
        except (ValueError, TypeError):
            errors.append('Amount must be a valid number.')
        
        # Date validation
        if post.get('date'):
            try:
                from datetime import datetime
                expense_date = datetime.strptime(post.get('date'), '%Y-%m-%d').date()
                today = datetime.now().date()
                if expense_date > today:
                    errors.append('Expense date cannot be in the future.')
            except ValueError:
                errors.append('Invalid date format.')
        
        # Duplicate expense detection
        if post.get('date') and post.get('total_amount') and post.get('category_id'):
            try:
                employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
                existing_expense = request.env['hr.expense'].sudo().search([
                    ('employee_id', '=', employee.id),
                    ('date', '=', post.get('date')),
                    ('total_amount', '=', float(post.get('total_amount'))),
                    ('product_id', '=', int(post.get('category_id'))),
                    ('sheet_id.state', '!=', 'cancel')  # Exclude withdrawn expenses
                ], limit=1)
                
                if existing_expense:
                    errors.append('A similar expense already exists for the same date, amount, and category. Please verify this is not a duplicate.')
                    _logger.warning("Potential duplicate expense detected for employee %s", employee.name)
                    
            except Exception as duplicate_check_error:
                _logger.warning("Error checking for duplicate expenses: %s", str(duplicate_check_error))
        
        # File validation
        attachment = request.httprequest.files.get('attachment')
        if attachment and attachment.filename:
            # Check file size (max 10MB)
            file_content = attachment.read()
            if len(file_content) > 10 * 1024 * 1024:
                errors.append('File size cannot exceed 10MB.')
            attachment.seek(0)  # Reset file pointer
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
            if attachment.content_type not in allowed_types:
                errors.append('Only JPG, PNG, and PDF files are allowed.')
        
        return errors
    
    def _get_or_create_expense_sheet(self, employee, expense):
        """Get existing draft sheet or create new one"""
        import logging
        _logger = logging.getLogger(__name__)
        
        company_id = employee.company_id.id
        
        # Find existing draft sheet in the same company
        sheet = request.env['hr.expense.sheet'].sudo().search([
            ('employee_id', '=', employee.id),
            ('company_id', '=', company_id),
            ('state', '=', 'draft')
        ], limit=1)
        
        if not sheet:
            # Create new sheet with company and currency info
            sheet_vals = {
                'name': f'Expense Report - {employee.name}',
                'employee_id': employee.id,
                'expense_line_ids': [(4, expense.id)],
                'company_id': company_id,
                'currency_id': employee.company_id.currency_id.id,
            }
            sheet = request.env['hr.expense.sheet'].sudo().create(sheet_vals)
            _logger.info("Created new expense sheet with ID: %d", sheet.id)
        else:
            # Add expense to existing sheet
            sheet.write({'expense_line_ids': [(4, expense.id)]})
            _logger.info("Added expense to existing sheet ID: %d", sheet.id)
        
        # Submit the sheet if it has expenses
        if sheet.state == 'draft' and sheet.expense_line_ids:
            try:
                sheet.action_submit_sheet()
                _logger.info("Successfully submitted expense sheet ID: %d", sheet.id)
            except Exception as submit_error:
                _logger.warning("Failed to auto-submit sheet: %s", str(submit_error))
        
        return sheet

    @http.route(MY_EMPLOYEE_URL + '/expenses/withdraw/<int:expense_id>', type='http', auth='user', website=True, methods=['POST'])
    def portal_expense_withdraw(self, expense_id, **post):
        import logging
        _logger = logging.getLogger(__name__)
        
        expense = request.env['hr.expense'].sudo().browse(expense_id)
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        
        # Only allow withdraw if expense is in submitted state and belongs to the current employee
        if expense and expense.employee_id.id == employee.id and expense.sheet_id and expense.sheet_id.state == 'submit':
            try:
                # Set the report to cancelled (withdraw)
                expense.sheet_id.write({'state': 'cancel'})
                _logger.info("Successfully withdrew expense ID: %d", expense_id)
            except Exception as withdraw_error:
                _logger.error("Failed to withdraw expense: %s", str(withdraw_error))
        
        return request.redirect(MY_EMPLOYEE_URL + '/expenses')

    @http.route(MY_EMPLOYEE_URL + '/expenses/receipt/<int:expense_id>', type='http', auth='user', website=True)
    def portal_expense_receipt(self, expense_id, **kwargs):
        """View expense receipt/attachment"""
        import logging
        _logger = logging.getLogger(__name__)
        
        expense = request.env['hr.expense'].sudo().browse(expense_id)
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        
        # Security check: only allow viewing own expense receipts
        if not expense or expense.employee_id.id != employee.id:
            return request.not_found()
        
        # Get the main attachment
        attachment = expense.message_main_attachment_id
        if not attachment:
            # If no main attachment is set, try to find any attachment related to this expense
            attachments = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'hr.expense'),
                ('res_id', '=', expense_id)
            ], limit=1)
            
            if attachments:
                attachment = attachments[0]
            else:
                return request.not_found()
        
        # Return the attachment data
        return request.env['ir.http'].with_context(attachment_token=attachment.access_token)._get_record_and_check(
            'ir.attachment', attachment.id
        )

    @http.route(MY_EMPLOYEE_URL + '/payslips', type='http', auth='user', website=True)
    @check_portal_access('payslip')
    def portal_payslip_history(self, **kwargs):
        """Portal route for viewing payslip history - Only confirmed payslips"""
        import logging
        _logger = logging.getLogger(__name__)
        
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect(MY_EMPLOYEE_URL)
            
        # Only show confirmed payslips - no status filter needed
        domain = [
            ('employee_id', '=', employee.id),
            ('state', 'in', ['done', 'paid'])
        ]
        
        # Only month/year filtering allowed
        month = kwargs.get('month')
        year = kwargs.get('year')
        
        # Log filter parameters for debugging
        _logger.info("Payslip filters - month: %s, year: %s", month, year)
        
        if month and year:
            try:
                # Filter by date range for selected month/year
                from datetime import datetime
                from calendar import monthrange
                start_date = datetime(int(year), int(month), 1)
                end_date = datetime(int(year), int(month), monthrange(int(year), int(month))[1], 23, 59, 59)
                domain += [('date_from', '>=', start_date.strftime('%Y-%m-%d')),
                          ('date_to', '<=', end_date.strftime('%Y-%m-%d'))]
                _logger.info("Date filter applied: %s to %s", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            except (ValueError, TypeError) as e:
                _logger.warning("Invalid date filter values - month: %s, year: %s, error: %s", month, year, e)
        
        _logger.info("Final domain: %s", domain)
        payslips = request.env['hr.payslip'].sudo().search(domain, order='date_from desc, date_to desc')
        _logger.info("Found %d confirmed payslips", len(payslips))
        
        # For dropdowns - get available years and months from payslips
        from datetime import datetime
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 2))
        months = [
            {'value': i, 'name': datetime(2000, i, 1).strftime('%B')} for i in range(1, 13)
        ]
        
        return request.render('employee_self_service_portal.portal_payslip', {
            'payslips': payslips,
            'employee': employee,
            'years': years,
            'months': months,
            'selected_month': month or '',
            'selected_year': year or '',
        })

    @http.route(MY_EMPLOYEE_URL + '/payslips/download/<int:payslip_id>', type='http', auth='user', website=True)
    def portal_payslip_download(self, payslip_id, **kwargs):
        """Download payslip as PDF"""
        import logging
        import base64
        _logger = logging.getLogger(__name__)
        
        try:
            payslip = request.env['hr.payslip'].sudo().browse(payslip_id)
            employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
            
            # Security check - only allow access to own payslips
            if not payslip.exists() or not employee or payslip.employee_id.id != employee.id:
                _logger.warning("Unauthorized payslip access attempt by user %s for payslip %s", request.uid, payslip_id)
                return request.redirect(MY_EMPLOYEE_URL + '/payslips?error=access_denied')
            
            # Only allow download of confirmed payslips
            if payslip.state not in ['done', 'paid']:
                _logger.warning("Download attempt for unconfirmed payslip %s by user %s", payslip_id, request.uid)
                return request.redirect(MY_EMPLOYEE_URL + '/payslips?error=not_confirmed')
            
            _logger.info("Attempting to download payslip %s for user %s", payslip_id, request.uid)
            
            # Try to find the payslip report - multiple approaches with detailed logging
            report_ref = None
            
            # Method 1: Try standard hr_payroll reports with sudo()
            report_names = [
                'hr_payroll.action_report_payslip',
                'hr_payroll.payslip_report', 
                'hr_payroll.report_payslip',
                'hr_payroll.report_payslip_details'
            ]
            
            for report_name in report_names:
                try:
                    report_ref = request.env.ref(report_name, raise_if_not_found=False)
                    if report_ref:
                        _logger.info("Found report reference: %s", report_name)
                        # Test if we can access this report
                        try:
                            report_sudo = report_ref.sudo()
                            # Try a quick test to see if this report can be used
                            if hasattr(report_sudo, 'report_name') or hasattr(report_sudo, '_render_qweb_pdf'):
                                _logger.info("Report %s is accessible and usable", report_name)
                                break
                            else:
                                _logger.warning("Report %s found but may not be usable", report_name)
                                report_ref = None
                        except Exception as access_test:
                            _logger.warning("Report %s access test failed: %s", report_name, str(access_test))
                            report_ref = None
                            continue
                    else:
                        _logger.debug("Report %s not found", report_name)
                except Exception as ref_error:
                    _logger.debug("Error checking report %s: %s", report_name, str(ref_error))
                    continue
            
            # Method 2: Search for payslip reports if standard ones not found
            if not report_ref:
                _logger.info("Standard reports not found, searching for any payslip reports...")
                try:
                    reports = request.env['ir.actions.report'].sudo().search([
                        ('model', '=', 'hr.payslip'),
                        ('report_type', '=', 'qweb-pdf')
                    ])
                    _logger.info("Found %d payslip reports in system", len(reports))
                    
                    for report in reports:
                        try:
                            # Test each report
                            _logger.info("Testing report: %s (ID: %d)", report.sudo().name, report.id)
                            report_ref = report
                            break
                        except Exception as test_error:
                            _logger.warning("Report test failed: %s", str(test_error))
                            continue
                            
                except Exception as search_error:
                    _logger.error("Error searching for reports: %s", str(search_error))
            
            if not report_ref:
                _logger.error("No payslip report found for model hr.payslip")
                return request.redirect(MY_EMPLOYEE_URL + '/payslips?error=report_not_found')
            
            # Generate PDF using the found report - use sudo() for report access
            _logger.info("Attempting to generate PDF with found report (ID: %d)", report_ref.id)
            
            # Use the correct method based on Odoo version with sudo()
            pdf_content = None
            try:
                report_sudo = report_ref.sudo()
                
                # Use the standard Odoo report rendering approach
                _logger.info("Using standard report rendering with payslip ID: %d", payslip.id)
                
                # Method 1: Try _render_qweb_pdf with proper context and parameters
                try:
                    # Use the correct Odoo 18 API for report rendering
                    # _render_qweb_pdf expects (report_ref, res_ids, data=None)
                    pdf_content, _ = report_sudo._render_qweb_pdf(report_sudo.report_name, payslip.ids)
                    _logger.info("Successfully used _render_qweb_pdf method")
                except Exception as method_error:
                    _logger.warning("_render_qweb_pdf failed: %s", str(method_error))
                    
                    # Method 2: Try with render_qweb_pdf (if available)
                    try:
                        # Try render_qweb_pdf method 
                        pdf_content, _ = report_sudo.render_qweb_pdf(payslip.ids)
                        _logger.info("Successfully used render_qweb_pdf method")
                    except Exception as method_error2:
                        _logger.warning("render_qweb_pdf method failed: %s", str(method_error2))
                        
                        # Method 3: Try with _render method (with proper parameters)
                        try:
                            # Use _render with proper report_name and res_ids parameters
                            pdf_content, _ = report_sudo._render(report_sudo.report_name, payslip.ids)
                            _logger.info("Successfully used _render method")
                        except Exception as method_error3:
                            _logger.error("All render methods failed: %s", str(method_error3))
                            raise Exception("All report render methods failed")
                
                if pdf_content and len(pdf_content) > 1000:
                    _logger.info("Successfully generated PDF using Odoo report, size: %d bytes", len(pdf_content))
                else:
                    _logger.warning("PDF content is empty or too small: %s bytes", len(pdf_content) if pdf_content else 0)
                    pdf_content = None
                    
            except Exception as render_error:
                _logger.error("PDF rendering failed with Odoo report: %s", str(render_error))
                pdf_content = None
            
            # Only use fallback if we couldn't get a valid PDF from Odoo reports
            if not pdf_content or len(pdf_content) < 100:
                _logger.warning("Odoo report failed or returned invalid PDF, using fallback method")
                
                # Fallback: Create a simple HTML-to-PDF conversion
                _logger.info("Attempting simple PDF generation as fallback")
                _logger.info("Attempting simple PDF generation as fallback")
                try:
                    # Create simple HTML content
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <title>Payslip {payslip.number or payslip.id}</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 20px; }}
                            .header {{ text-align: center; margin-bottom: 30px; }}
                            .info {{ margin-bottom: 20px; }}
                            .line {{ margin: 5px 0; }}
                            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                            th {{ background-color: #f2f2f2; }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>PAYSLIP</h1>
                            <h2>{payslip.number or payslip.id}</h2>
                        </div>
                        
                        <div class="info">
                            <div class="line"><strong>Employee:</strong> {payslip.employee_id.name}</div>
                            <div class="line"><strong>Period:</strong> {payslip.date_from} to {payslip.date_to}</div>
                            <div class="line"><strong>Status:</strong> {dict(payslip._fields['state'].selection).get(payslip.state, payslip.state)}</div>
                        </div>
                        
                        <table>
                            <thead>
                                <tr>
                                    <th>Description</th>
                                    <th>Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
                    
                    # Add payslip lines
                    if payslip.line_ids:
                        for line in payslip.line_ids:
                            html_content += f"""
                                <tr>
                                    <td>{line.name}</td>
                                    <td>{line.total:.2f}</td>
                                </tr>
                            """
                    else:
                        html_content += "<tr><td colspan='2'>No payslip details available</td></tr>"
                    
                    html_content += """
                            </tbody>
                        </table>
                    </body>
                    </html>
                    """
                    
                    # Use wkhtmltopdf if available, otherwise create simple text-based PDF
                    try:
                        import subprocess
                        import tempfile
                        import os
                        
                        # Create temporary HTML file
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as html_file:
                            html_file.write(html_content)
                            html_file_path = html_file.name
                        
                        # Create temporary PDF file
                        pdf_file_path = html_file_path.replace('.html', '.pdf')
                        
                        # Try wkhtmltopdf
                        result = subprocess.run([
                            'wkhtmltopdf', '--page-size', 'A4', '--orientation', 'Portrait',
                            html_file_path, pdf_file_path
                        ], capture_output=True, timeout=30)
                        
                        if result.returncode == 0 and os.path.exists(pdf_file_path):
                            with open(pdf_file_path, 'rb') as pdf_file:
                                pdf_content = pdf_file.read()
                            _logger.info("Successfully created PDF using wkhtmltopdf")
                        else:
                            raise Exception("wkhtmltopdf failed")
                            
                        # Cleanup
                        os.unlink(html_file_path)
                        os.unlink(pdf_file_path)
                        
                    except Exception:
                        # Final fallback: Create a very simple text-based response
                        _logger.warning("wkhtmltopdf not available, creating simple text response")
                        simple_content = f"""
PAYSLIP: {payslip.number or payslip.id}
Employee: {payslip.employee_id.name}
Period: {payslip.date_from} to {payslip.date_to}
Status: {dict(payslip._fields['state'].selection).get(payslip.state, payslip.state)}

Payslip Details:
"""
                        if payslip.line_ids:
                            for line in payslip.line_ids:
                                simple_content += f"{line.name}: {line.total:.2f}\n"
                        else:
                            simple_content += "No payslip details available\n"
                        
                        # Return as text file instead of PDF
                        safe_number = (payslip.number or str(payslip.id)).replace('/', '_').replace('\\', '_')
                        safe_date = payslip.date_from.strftime('%Y-%m') if payslip.date_from else 'unknown'
                        filename = f"Payslip_{safe_number}_{safe_date}.txt"
                        
                        headers = [
                            ('Content-Type', 'text/plain'),
                            ('Content-Length', len(simple_content.encode('utf-8'))),
                            ('Content-Disposition', f'attachment; filename="{filename}"'),
                            ('Cache-Control', 'no-cache'),
                            ('Pragma', 'no-cache')
                        ]
                        
                        _logger.info("Payslip %s downloaded as text file by user %s", payslip_id, request.uid)
                        return request.make_response(simple_content.encode('utf-8'), headers=headers)
                        
                except Exception as fallback_error:
                    _logger.error("Fallback PDF generation also failed: %s", str(fallback_error))
                    return request.redirect(MY_EMPLOYEE_URL + '/payslips?error=render_failed')
            
            if not pdf_content:
                _logger.error("All PDF generation methods failed - no content generated")
                return request.redirect(MY_EMPLOYEE_URL + '/payslips?error=empty_pdf')
            
            # Log which method was used
            if len(pdf_content) > 1000:
                _logger.info("Successfully generated PDF - likely from Odoo report system (%d bytes)", len(pdf_content))
            else:
                _logger.info("Generated small PDF - likely from fallback method (%d bytes)", len(pdf_content))
            
            # Create safe filename
            safe_number = (payslip.number or str(payslip.id)).replace('/', '_').replace('\\', '_')
            safe_date = payslip.date_from.strftime('%Y-%m') if payslip.date_from else 'unknown'
            filename = f"Payslip_{safe_number}_{safe_date}.pdf"
            
            # Create response with PDF
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf_content)),
                ('Content-Disposition', f'attachment; filename="{filename}"'),
                ('Cache-Control', 'no-cache'),
                ('Pragma', 'no-cache')
            ]
            
            _logger.info("Payslip %s downloaded successfully by user %s, file size: %d bytes", 
                        payslip_id, request.uid, len(pdf_content))
            
            return request.make_response(pdf_content, headers=pdfhttpheaders)
            
        except Exception as e:
            _logger.error("Unexpected error in payslip download for payslip %s: %s", payslip_id, str(e))
            import traceback
            _logger.error("Full traceback: %s", traceback.format_exc())
            return request.redirect(MY_EMPLOYEE_URL + '/payslips?error=download_failed')

    @http.route(MY_EMPLOYEE_URL + '/payslips/view/<int:payslip_id>', type='http', auth='user', website=True)
    def portal_payslip_view(self, payslip_id, **kwargs):
        """View payslip details"""
        payslip = request.env['hr.payslip'].sudo().browse(payslip_id)
        employee = request.env[HR_EMPLOYEE_MODEL].sudo().search([('user_id', '=', request.uid)], limit=1)
        
        # Security check - only allow access to own payslips
        if not payslip or not employee or payslip.employee_id.id != employee.id:
            return request.redirect(MY_EMPLOYEE_URL + '/payslips')
            
        return request.render('employee_self_service_portal.portal_payslip_view', {
            'payslip': payslip,
            'employee': employee,
        })

    @http.route('/my/employee/crm/update_stage/<int:lead_id>', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_employee_crm_update_stage(self, lead_id, **post):
        """Route to handle stage updates via AJAX"""
        import json
        
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        
        # Security check - only allow access to own leads
        if not lead or lead.user_id.id != user.id:
            response = json.dumps({'success': False, 'error': 'Access denied'})
            return request.make_response(response, headers={'Content-Type': 'application/json'})
        
        stage_id = post.get('stage_id')
        if not stage_id:
            response = json.dumps({'success': False, 'error': 'Stage ID is required'})
            return request.make_response(response, headers={'Content-Type': 'application/json'})
        
        try:
            stage_id = int(stage_id)
            stage = request.env['crm.stage'].sudo().browse(stage_id)
            if not stage.exists():
                response = json.dumps({'success': False, 'error': 'Invalid stage'})
                return request.make_response(response, headers={'Content-Type': 'application/json'})
            
            lead.write({'stage_id': stage_id})
            response = json.dumps({'success': True, 'stage_name': stage.name})
            return request.make_response(response, headers={'Content-Type': 'application/json'})
            
        except Exception as e:
            _logger.error("Error updating lead stage: %s", str(e))
            response = json.dumps({'success': False, 'error': 'Update failed'})
            return request.make_response(response, headers={'Content-Type': 'application/json'})

    @http.route('/my/employee/crm/api/kpis', type='http', auth='user', website=True, methods=['GET'], csrf=False)
    def portal_employee_crm_api_kpis(self, **kwargs):
        """API endpoint to get dashboard KPIs"""
        import json
        from datetime import date
        
        user = request.env.user
        
        try:
            # Get all user leads
            all_user_leads = request.env['crm.lead'].sudo().search([('user_id', '=', user.id)])
            today = date.today()
            
            # Calculate KPIs
            kpis = self._calculate_dashboard_kpis(all_user_leads, today)
            
            response = json.dumps({'success': True, 'kpis': kpis})
            return request.make_response(response, headers={'Content-Type': 'application/json'})
            
        except Exception as e:
            _logger.error("Error fetching KPIs: %s", str(e))
            response = json.dumps({'success': False, 'error': 'Failed to fetch KPIs'})
            return request.make_response(response, headers={'Content-Type': 'application/json'})

    @http.route('/my/employee/crm/api/quick_action', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_employee_crm_quick_action(self, **post):
        """API endpoint for quick actions on leads"""
        import json
        
        user = request.env.user
        action = post.get('action')
        lead_id = post.get('lead_id')
        
        try:
            lead_id = int(lead_id)
            lead = request.env['crm.lead'].sudo().browse(lead_id)
            
            # Security check
            if not lead or lead.user_id.id != user.id:
                response = json.dumps({'success': False, 'error': 'Access denied'})
                return request.make_response(response, headers={'Content-Type': 'application/json'})
            
            if action == 'mark_won':
                # Find "Won" stage
                won_stage = request.env['crm.stage'].sudo().search([('name', '=ilike', 'won')], limit=1)
                if won_stage:
                    lead.write({'stage_id': won_stage.id})
                    response = json.dumps({'success': True, 'message': 'Lead marked as won'})
                else:
                    response = json.dumps({'success': False, 'error': 'Won stage not found'})
                    
            elif action == 'mark_lost':
                # Find "Lost" stage or set as lost
                lost_stage = request.env['crm.stage'].sudo().search([('name', '=ilike', 'lost')], limit=1)
                if lost_stage:
                    lead.write({'stage_id': lost_stage.id})
                else:
                    # Use Odoo's built-in lost functionality
                    lead.write({'active': False})
                response = json.dumps({'success': True, 'message': 'Lead marked as lost'})
                
            elif action == 'schedule_call':
                # Create a call activity
                activity_type = request.env['mail.activity.type'].sudo().search([('name', '=ilike', 'call')], limit=1)
                if not activity_type:
                    activity_type = request.env['mail.activity.type'].sudo().search([], limit=1)
                    
                if activity_type:
                    from datetime import date, timedelta
                    request.env['mail.activity'].sudo().create({
                        'res_id': lead.id,
                        'res_model_id': request.env['ir.model']._get('crm.lead').id,
                        'activity_type_id': activity_type.id,
                        'summary': 'Scheduled Call',
                        'date_deadline': date.today() + timedelta(days=1),
                        'user_id': user.id,
                    })
                    response = json.dumps({'success': True, 'message': 'Call scheduled for tomorrow'})
                else:
                    response = json.dumps({'success': False, 'error': 'Could not create activity'})
                    
            elif action == 'add_note':
                note_content = post.get('note_content', '')
                if note_content:
                    lead.message_post(body=note_content, message_type='comment')
                    response = json.dumps({'success': True, 'message': 'Note added'})
                else:
                    response = json.dumps({'success': False, 'error': 'Note content required'})
                    
            else:
                response = json.dumps({'success': False, 'error': 'Unknown action'})
                
            return request.make_response(response, headers={'Content-Type': 'application/json'})
            
        except Exception as e:
            _logger.error("Error in quick action: %s", str(e))
            response = json.dumps({'success': False, 'error': 'Action failed'})
            return request.make_response(response, headers={'Content-Type': 'application/json'})

    @http.route('/my/employee/crm/notes_modal/<int:lead_id>', type='http', auth='user', website=True)
    def portal_employee_crm_notes_modal(self, lead_id, **kwargs):
        """Route to handle notes modal content loading"""
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        user = request.env.user
        
        # Security check - only allow access to own leads
        if not lead or lead.user_id.id != user.id:
            return '<div class="alert alert-danger">Access denied</div>'
        
        # Get all log notes for this lead
        notes = request.env['mail.message'].sudo().search([
            ('model', '=', 'crm.lead'),
            ('res_id', '=', lead_id),
            ('message_type', '=', 'comment'),
            ('subtype_id', '=', request.env.ref('mail.mt_note').id)
        ], order='date desc')
        
        context = {
            'lead': lead,
            'notes': notes,
        }
        
        return request.render('employee_self_service_portal.portal_employee_crm_notes_modal', context)
