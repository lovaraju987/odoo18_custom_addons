# -*- coding: utf-8 -*-
# from odoo import http


# class EmployeeShiftReport(http.Controller):
#     @http.route('/employee_shift_report/employee_shift_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_shift_report/employee_shift_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_shift_report.listing', {
#             'root': '/employee_shift_report/employee_shift_report',
#             'objects': http.request.env['employee_shift_report.employee_shift_report'].search([]),
#         })

#     @http.route('/employee_shift_report/employee_shift_report/objects/<model("employee_shift_report.employee_shift_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_shift_report.object', {
#             'object': obj
#         })

