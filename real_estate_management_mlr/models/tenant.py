from odoo import models, fields


class Tenant(models.Model):
    _name = 'real.estate.tenant'
    _description = 'Tenant'

    name = fields.Char(string='Tenant Name', required=True)
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    leases = fields.One2many('real.estate.lease', 'tenant_id', string='Leases')
    image_1920 = fields.Image(
        'Profile Picture',
        max_width=1920,
        max_height=1920,
    )
    occupation = fields.Char('Occupation')
    birthdate = fields.Date('Birthdate')
