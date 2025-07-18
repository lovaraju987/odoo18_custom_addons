# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RealEstate(models.Model):

    _name = "real.estate"
    _inherit = "realestate.abstract.entity"
    _description = "Real Estate"

    # Odoo 18 compatibility: cleaned for deprecated args, added string attributes, ordering
    type_id = fields.Many2one(
        comodel_name="real.estate.type", required=True, ondelete="restrict", index=True, string="Property Type"
    )
    ref = fields.Char(
        default=lambda self: self.env["ir.sequence"].next_by_code("real.estate"),
        string="Reference",
        index=True,
        copy=False,
        readonly=True,
    )
    short_description = fields.Char(translate=True, string="Short Description")
    description = fields.Text(translate=True, string="Long Description")

    _order = "ref desc, id desc"
