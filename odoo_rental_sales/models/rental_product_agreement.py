# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models


class RentalProductAgreement(models.Model):
    """Created the class for creating the model rental product agreement"""
    _name = 'rental.product.agreement'
    _description = 'Rental Product Agreement'

    name = fields.Char(string='Name', required=True,
                       help='Name of the rental product agreement')
    sequence = fields.Integer(string='Sequence', required=True,
                              help='Sequence of the rental product agreement')
    description = fields.Text(string='Description',
                              help='Description of the rental product agreement')
    agreement_file = fields.Binary(string='Product Agreement',
                                   help='Agreement file of the rental product')
