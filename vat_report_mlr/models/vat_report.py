from odoo import models, fields, api
from odoo import api, SUPERUSER_ID

class VatReturnReport(models.TransientModel):
    _name = 'vat.return.report'
    _description = 'VAT Return Report'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    vat_lines = fields.Json(string='VAT Lines', compute='_compute_vat_lines')

    @api.depends('date_from', 'date_to')
    def _compute_vat_lines(self):
        for wizard in self:
            moves = self.env['account.move'].search([
                ('date', '>=', wizard.date_from),
                ('date', '<=', wizard.date_to),
                ('move_type', 'in', ['out_invoice', 'in_invoice']),
                ('state', '=', 'posted'),
            ])
            lines = []
            for move in moves:
                for line in move.line_ids.filtered(lambda l: l.tax_ids):
                    lines.append({
                        'date': str(move.date),
                        'partner': move.partner_id.name,
                        'tax': ', '.join(line.tax_ids.mapped('name')),
                        'amount': line.tax_base_amount,
                    })
            wizard.vat_lines = lines

    def print_report(self):
        self.ensure_one()
        return self.env.ref('vat_report_mlr.action_report_vat_return').report_action(self)

def post_init_hook(env):
    # Remove any existing report action with the same xml_id
    old_report = env['ir.actions.report'].search([('report_name', '=', 'vat_report_mlr.report_vat_return')])
    if old_report:
        old_report.unlink()
    # Create the report action
    report_action = env['ir.actions.report'].create({
        'name': 'VAT Return Report',
        'model': 'vat.return.report',
        'report_type': 'qweb-pdf',
        'report_name': 'vat_report_mlr.report_vat_return',
        'print_report_name': "'VAT Return Report - %s' % (object.date_from)",
        'binding_model_id': env['ir.model']._get_id('vat.return.report'),
        'binding_type': 'report',
    })
    # Register the external ID for the report action
    env['ir.model.data'].create({
        'name': 'action_report_vat_return',
        'model': 'ir.actions.report',
        'module': 'vat_report_mlr',
        'res_id': report_action.id,
        'noupdate': True,
    })
