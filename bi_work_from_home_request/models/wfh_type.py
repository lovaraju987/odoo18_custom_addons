# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class WFHType(models.Model):
    _name = 'wfh.type'
    _description = 'Work From Home Type'
    _rec_name='name'

    name = fields.Char(string='Name')
    approval = fields.Selection(
        [('by_manager', 'By Employee Manager'), ('by_officer', 'By Employee Manager and Time Off Officer')],
        default='by_manager')
    user_id = fields.Many2one('res.users', string='Responsible Time Off Officer')
    monthly_limit = fields.Integer(string="Work From Home Monthly Limit")
