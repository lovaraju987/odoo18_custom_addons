# controllers/main.py
from odoo import http, fields
from odoo.http import request

class PortalEmployee(http.Controller):

    @http.route('/my/employee', type='http', auth='user', website=True)
    def portal_employee_profile(self, **kwargs):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)], limit=1)
        return request.render('employee_self_service_portal.portal_employee_profile', {'employee': employee})

    @http.route('/my/employee/attendance/checkin', type='http', auth='user', methods=['POST'], website=True)
    def check_in(self, **post):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect('/my/employee')
        try:
            request.env['hr.attendance'].sudo().create({
                'employee_id': employee.id,
                'check_in': fields.Datetime.now(),
            })
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Check-in failed: %s", e)
            return request.redirect('/my/employee')
        return request.redirect('/my/employee/attendance')

    @http.route('/my/employee/attendance/checkout', type='http', auth='user', methods=['POST'], website=True)
    def check_out(self, **post):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect('/my/employee')
        last_attendance = request.env['hr.attendance'].sudo().search(
            [('employee_id', '=', employee.id)], order='check_in desc', limit=1)
        if last_attendance and not last_attendance.check_out:
            last_attendance.check_out = fields.Datetime.now()
        return request.redirect('/my/employee/attendance')
    
    @http.route('/my/employee/attendance', type='http', auth='user', website=True)
    def portal_attendance_history(self, **kwargs):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)], limit=1)
        attendances = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id)
        ], order='check_in desc', limit=20)
        return request.render('employee_self_service_portal.portal_attendance', {
            'attendances': attendances,
            'employee': employee,
        })

    @http.route('/my/employee/edit', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_edit(self, **post):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)], limit=1)
        if not employee:
            return request.redirect('/my/employee')
        if http.request.httprequest.method == 'POST':
            vals = {}
            if post.get('work_email'):
                vals['work_email'] = post.get('work_email')
            if post.get('work_phone'):
                vals['work_phone'] = post.get('work_phone')
            if post.get('address_home_id'):
                vals['address_home_id'] = int(post.get('address_home_id'))
            if vals:
                employee.sudo().write(vals)
            return request.redirect('/my/employee')
        return request.render('employee_self_service_portal.portal_employee_edit', {
            'employee': employee,
        })

    @http.route('/my/ess', type='http', auth='user', website=True)
    def portal_ess_dashboard(self, **kwargs):
        return request.render('employee_self_service_portal.portal_ess_dashboard')
