# -*- coding: utf-8 -*-
# from odoo import http


# class ApiManagement(http.Controller):
#     @http.route('/api_management/api_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/api_management/api_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('api_management.listing', {
#             'root': '/api_management/api_management',
#             'objects': http.request.env['api_management.api_management'].search([]),
#         })

#     @http.route('/api_management/api_management/objects/<model("api_management.api_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('api_management.object', {
#             'object': obj
#         })

