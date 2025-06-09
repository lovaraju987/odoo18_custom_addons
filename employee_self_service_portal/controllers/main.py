# controllers/main.py
from odoo import http, fields
from odoo.http import request

class PortalEmployee(http.Controller):
    def _get_employee(self):
        return request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)], limit=1)

    @http.route('/my/employee', type='http', auth='user', website=True)
    def portal_employee_profile(self, **kw):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)], limit=1)
        return request.render('employee_self_service_portal.portal_employee_profile_personal', {
            'employee': employee,
            'section': 'personal',
        })

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
            return request.redirect('/my/employee')
        return request.render('employee_self_service_portal.portal_employee_edit', {
            'employee': employee,
        })

    @http.route('/my/ess', type='http', auth='user', website=True)
    def portal_ess_dashboard(self, **kwargs):
        return request.render('employee_self_service_portal.portal_ess_dashboard')

    @http.route('/my/employee/personal', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_personal(self, **post):
        employee = self._get_employee()
        if request.httprequest.method == 'POST':
            # update personal details
            vals = {
                'work_email': post.get('work_email'),
                'work_phone': post.get('work_phone'),
                'birthday': post.get('birthday'),
                'gender': post.get('gender'),
                'marital': post.get('marital'),
            }
            employee.sudo().write({k: v for k, v in vals.items() if v is not None})
        return request.render('employee_self_service_portal.portal_employee_profile_personal', {
            'employee': employee,
            'section': 'personal',
        })

    @http.route('/my/employee/experience', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_employee_experience(self, **post):
        employee = self._get_employee()
        if request.httprequest.method == 'POST':
            vals = {
                'x_experience': post.get('x_experience'),
                'x_skills': post.get('x_skills'),
            }
            employee.sudo().write({k: v for k, v in vals.items() if v is not None})
        return request.render('employee_self_service_portal.portal_employee_profile_experience', {
            'employee': employee,
            'section': 'experience',
        })

    @http.route('/my/employee/certification', type='http', auth='user', website=True, methods=['GET', 'POST'])
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

    @http.route('/my/employee/bank', type='http', auth='user', website=True, methods=['GET', 'POST'])
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

    @http.route('/my/employee/tasks', type='http', auth='user', website=True)
    def portal_employee_tasks(self, **kwargs):
        employee = self._get_employee()
        user = request.env.user
        tasks = request.env['project.task'].sudo().search([
            ('user_ids', 'in', [user.id])
        ], order='date_deadline asc, priority desc')
        return request.render('employee_self_service_portal.portal_employee_tasks', {
            'employee': employee,
            'tasks': tasks,
        })
