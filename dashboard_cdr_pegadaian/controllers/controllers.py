# -*- coding: utf-8 -*-
# from odoo import http


# class DashboardCdrPegadaian(http.Controller):
#     @http.route('/dashboard_cdr_pegadaian/dashboard_cdr_pegadaian', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dashboard_cdr_pegadaian/dashboard_cdr_pegadaian/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('dashboard_cdr_pegadaian.listing', {
#             'root': '/dashboard_cdr_pegadaian/dashboard_cdr_pegadaian',
#             'objects': http.request.env['dashboard_cdr_pegadaian.dashboard_cdr_pegadaian'].search([]),
#         })

#     @http.route('/dashboard_cdr_pegadaian/dashboard_cdr_pegadaian/objects/<model("dashboard_cdr_pegadaian.dashboard_cdr_pegadaian"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dashboard_cdr_pegadaian.object', {
#             'object': obj
#         })
