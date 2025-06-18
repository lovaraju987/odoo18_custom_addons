from odoo import models, fields, api
from odoo import api, SUPERUSER_ID
import io
import base64

class VatReturnReport(models.TransientModel):
    _name = 'vat.return.report'
    _description = 'VAT Return Report'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    vat_lines = fields.Json(string='VAT Lines', compute='_compute_vat_lines')
    excel_file = fields.Binary(string='Excel File', readonly=True)

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

    def export_excel_report(self):
        import xlsxwriter
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('VAT-201')

        # Header
        worksheet.write('A1', 'Company:')
        worksheet.write('B1', self.env.company.name)
        worksheet.write('A2', 'TRN:')
        worksheet.write('B2', self.env.company.vat or '')
        worksheet.write('A3', 'Period:')
        worksheet.write('B3', f'{self.date_from} to {self.date_to}')

        row = 5
        worksheet.write(row, 0, 'Type')
        worksheet.write(row, 1, 'Base Amount')
        worksheet.write(row, 2, 'Tax Amount')
        row += 1

        # Sales
        sales_lines = self._get_vat_lines('out_invoice')
        for line in sales_lines:
            worksheet.write(row, 0, line['tax'])
            worksheet.write(row, 1, line['base'])
            worksheet.write(row, 2, line['amount'])
            row += 1

        # Purchases
        row += 2
        worksheet.write(row, 0, 'Purchases')
        row += 1
        purchase_lines = self._get_vat_lines('in_invoice')
        for line in purchase_lines:
            worksheet.write(row, 0, line['tax'])
            worksheet.write(row, 1, line['base'])
            worksheet.write(row, 2, line['amount'])
            row += 1

        workbook.close()
        output.seek(0)
        self.excel_file = base64.b64encode(output.read())
        output.close()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model={self._name}&id={self.id}&field=excel_file&download=true&filename=vat_201_report.xlsx',
            'target': 'self',
        }

    def _get_vat_lines(self, move_type):
        moves = self.env['account.move'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('move_type', '=', move_type),
            ('state', '=', 'posted'),
        ])
        result = {}
        for move in moves:
            for line in move.line_ids.filtered(lambda l: l.tax_ids):
                for tax in line.tax_ids:
                    key = tax.name
                    if key not in result:
                        result[key] = {'tax': key, 'base': 0.0, 'amount': 0.0}
                    result[key]['base'] += line.tax_base_amount
                    result[key]['amount'] += line.tax_amount
        return list(result.values())

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
