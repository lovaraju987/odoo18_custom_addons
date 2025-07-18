# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class RealEstateAbstractEntity(models.AbstractModel):
    child_ids = fields.One2many('res.partner', 'parent_id', related="partner_id.child_ids", store=True, readonly=False)
    street = fields.Char(related="partner_id.street", store=True, readonly=False)
    street2 = fields.Char(related="partner_id.street2", store=True, readonly=False)
    city = fields.Char(related="partner_id.city", store=True, readonly=False)
    state_id = fields.Many2one('res.country.state', related="partner_id.state_id", store=True, readonly=False)
    zip = fields.Char(related="partner_id.zip", store=True, readonly=False)
    country_id = fields.Many2one('res.country', related="partner_id.country_id", store=True, readonly=False)
    category_id = fields.Many2many(related="partner_id.category_id", store=True, readonly=False)
    lang = fields.Selection(related="partner_id.lang", store=True, readonly=False)
    phone = fields.Char(related="partner_id.phone", store=True, readonly=False)
    mobile = fields.Char(related="partner_id.mobile", store=True, readonly=False)
    email = fields.Char(related="partner_id.email", store=True, readonly=False)
    _name = "realestate.abstract.entity"
    _description = "RealEstate Abstract Entity"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread"]

    active = fields.Boolean(default=True,)
    partner_id = fields.Many2one(
        string="Related Partner",
        comodel_name="res.partner",
        required=True,
        ondelete="cascade",
        index=True,
    )
    type = fields.Selection(
        default=lambda s: s._name, related="partner_id.type", readonly=False,
    )

    @api.model
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        vals = self._create_vals(vals)
        self_context = self
        if "type" in vals:
            self_context = self.with_context(default_type=vals.get("type"))
        return super(RealEstateAbstractEntity, self_context).create(vals)

    @api.model
    def _create_vals(self, vals):
        """ Override this in child classes in order to add default values. """
        return vals
