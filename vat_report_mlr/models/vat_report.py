from odoo import models, fields, api
import io, base64
from datetime import datetime

class VatReturnReport(models.TransientModel):
    _name = 'vat.return.report'
    _description = 'VAT Return Report'

    date_from       = fields.Date(string='Start Date', required=True)
    date_to         = fields.Date(string='End Date',   required=True)
    excel_file      = fields.Binary(string='VAT-201 Excel')
    excel_filename  = fields.Char(string='Filename')

    @api.depends('date_from', 'date_to')
    def _compute_vat_lines(self):
        # not used in Excel export, but kept for PDF
        for wiz in self:
            wiz.vat_lines = wiz._get_vat_lines('all')

    def _get_vat_lines(self, move_type):
        """ Return list of dicts with keys: tax, base, amount """
        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                  ('state', '=', 'posted')]
        if move_type == 'out_invoice':
            domain.append(('move_type', 'in', ['out_invoice']))
        elif move_type == 'in_invoice':
            domain.append(('move_type', 'in', ['in_invoice']))
        # else 'all' returns both; filter by tax_codes afterwards if needed
        moves = self.env['account.move'].search(domain)
        lines = {}
        for m in moves:
            for l in m.line_ids.filtered('tax_ids'):
                for t in l.tax_ids:
                    key = t.name
                    lines.setdefault(key, {'tax': key, 'base': 0.0, 'amount': 0.0})
                    lines[key]['base']   += l.tax_base_amount
                    # Use the tax line's balance as VAT amount
                    tax_line = m.line_ids.filtered(lambda x: x.tax_line_id == t)
                    vat_amount = sum(tl.balance for tl in tax_line)
                    lines[key]['amount'] += vat_amount
        return list(lines.values())

    def export_excel_report(self):
        import xlsxwriter
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # === Formats ===
        title_fmt    = workbook.add_format({
            'bold': True, 'font_size': 16, 'align': 'center',
            'bg_color': '#4F4F4F', 'font_color': '#FFFFFF'})
        section_fmt  = workbook.add_format({'bold': True, 'bg_color': '#D9E1F5','border':1})
        header_fmt   = workbook.add_format({'bold': True, 'bg_color': '#BDD7EE','border':1})
        text_fmt     = workbook.add_format({'border':1})
        curr_fmt     = workbook.add_format({'num_format':'"AED"#,##0.00','border':1})
        footer_fmt   = workbook.add_format({'italic':True,'font_size':10})

        # === Main sheet ===
        sht = workbook.add_worksheet('VAT 201- VAT Return')
        sht.set_column('A:F',20)
        sht.merge_range('A1:F1', 'VAT 201 Report', title_fmt)

        # Taxable Person Details
        sht.merge_range('A3:F3','Taxable Person Details', section_fmt)
        sht.write('A4', 'TRN', header_fmt);    sht.write('B4', self.env.company.vat or '', text_fmt)
        sht.write('A5', 'Name', header_fmt);   sht.write('B5', self.env.company.name, text_fmt)
        sht.write('A6', 'VAT 201 Period', header_fmt); sht.write('B6', f'{self.date_from} to {self.date_to}', text_fmt)
        sht.write('A7', 'Tax Year', header_fmt);     sht.write('B7', str(self.date_from.year), text_fmt)

        # Sales section
        row = 9
        sht.merge_range(row,0,row,5,'VAT on Sales and All Other Outputs', section_fmt); row+=1
        for col, val in enumerate(['Line','Name','Amount(AED)','VAT Amount(AED)','Adjustment(AED)']):
            sht.write(row, col, val, header_fmt)
        row+=1
        sales = self._get_vat_lines('out_invoice')
        sale_start = row
        for i, ln in enumerate(sales,1):
            sht.write(row, 0, f'{i}a', text_fmt)
            sht.write(row, 1, ln['tax'], text_fmt)
            sht.write(row, 2, ln['base'], curr_fmt)
            sht.write(row, 3, ln['amount'], curr_fmt)
            sht.write(row, 4, '', text_fmt)
            row+=1
        sht.write(row,1,'Total',section_fmt)
        sht.write_formula(row,2,f'=SUM(C{sale_start+1}:C{row})',curr_fmt)
        sht.write_formula(row,3,f'=SUM(D{sale_start+1}:D{row})',curr_fmt)
        row+=2

        # Purchase section
        sht.merge_range(row,0,row,5,'VAT on Expenses and All Other Inputs', section_fmt); row+=1
        for col, val in enumerate(['Line','Name','Amount(AED)','VAT Amount(AED)','Adjustment(AED)']):
            sht.write(row, col, val, header_fmt)
        row+=1
        purchases = self._get_vat_lines('in_invoice')
        pur_start = row
        for i, ln in enumerate(purchases,9):
            sht.write(row, 0, str(i), text_fmt)
            sht.write(row, 1, ln['tax'], text_fmt)
            sht.write(row, 2, ln['base'], curr_fmt)
            sht.write(row, 3, ln['amount'], curr_fmt)
            sht.write(row, 4, '', text_fmt)
            row+=1
        sht.write(row,1,'Totals',section_fmt)
        sht.write_formula(row,2,f'=SUM(C{pur_start+1}:C{row})',curr_fmt)
        sht.write_formula(row,3,f'=SUM(D{pur_start+1}:D{row})',curr_fmt)
        row+=2

        # Summary
        sht.merge_range(row,0,row,5,'Summary', section_fmt); row+=1
        sht.write(row,0,'NET VAT Due', header_fmt)
        sht.write_formula(row,2,f'=D{sale_start+len(sales)+1}-D{pur_start+len(purchases)+1}',curr_fmt)
        row+=1
        sht.write(row,0,'Total value of due tax for the period',header_fmt)
        sht.write_formula(row,2,f'=D{sale_start+len(sales)+1}',curr_fmt)
        row+=1
        sht.write(row,0,'Total value of recoverable tax for the period',header_fmt)
        sht.write_formula(row,2,f'=D{pur_start+len(purchases)+1}',curr_fmt)
        row+=1
        sht.write(row,0,'Payable Tax for the period',header_fmt)
        sht.write_formula(row,2,f'=C{row-2}-C{row-1}',curr_fmt)

        # Footer
        sht.write(row+2,0,
            f'Report generated by Odoo 18 on {datetime.now():%Y-%m-%d %H:%M:%S}', footer_fmt)

        # === Sales Sheet ===
        sales_ws = workbook.add_worksheet('Sales')
        sales_ws.set_column('A:F', 20)
        sales_headers = ['Date', 'Invoice', 'Customer', 'Tax', 'Base Amount (AED)', 'VAT Amount (AED)']
        for col, val in enumerate(sales_headers):
            sales_ws.write(0, col, val, header_fmt)
        sales_moves = self.env['account.move'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice')
        ])
        row = 1
        for move in sales_moves:
            for line in move.line_ids.filtered('tax_ids'):
                for tax in line.tax_ids:
                    # Find the tax line for this tax
                    tax_line = move.line_ids.filtered(lambda x: x.tax_line_id == tax)
                    vat_amount = sum(tl.balance for tl in tax_line)
                    sales_ws.write(row, 0, str(move.date), text_fmt)
                    sales_ws.write(row, 1, move.name or '', text_fmt)
                    sales_ws.write(row, 2, move.partner_id.name or '', text_fmt)
                    sales_ws.write(row, 3, tax.name, text_fmt)
                    sales_ws.write(row, 4, line.tax_base_amount, curr_fmt)
                    sales_ws.write(row, 5, vat_amount, curr_fmt)
                    row += 1

        # === Purchase Sheet ===
        purchase_ws = workbook.add_worksheet('Purchase')
        purchase_ws.set_column('A:F', 20)
        purchase_headers = ['Date', 'Bill', 'Vendor', 'Tax', 'Base Amount (AED)', 'VAT Amount (AED)']
        for col, val in enumerate(purchase_headers):
            purchase_ws.write(0, col, val, header_fmt)
        purchase_moves = self.env['account.move'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'posted'),
            ('move_type', '=', 'in_invoice')
        ])
        row = 1
        for move in purchase_moves:
            for line in move.line_ids.filtered('tax_ids'):
                for tax in line.tax_ids:
                    tax_line = move.line_ids.filtered(lambda x: x.tax_line_id == tax)
                    vat_amount = sum(tl.balance for tl in tax_line)
                    purchase_ws.write(row, 0, str(move.date), text_fmt)
                    purchase_ws.write(row, 1, move.name or '', text_fmt)
                    purchase_ws.write(row, 2, move.partner_id.name or '', text_fmt)
                    purchase_ws.write(row, 3, tax.name, text_fmt)
                    purchase_ws.write(row, 4, line.tax_base_amount, curr_fmt)
                    purchase_ws.write(row, 5, vat_amount, curr_fmt)
                    row += 1

        # === Other Voucher Sheet ===
        voucher_ws = workbook.add_worksheet('Other Voucher')
        voucher_ws.set_column('A:G', 20)
        voucher_headers = ['Date', 'Entry', 'Partner', 'Type', 'Tax', 'Base Amount (AED)', 'VAT Amount (AED)']
        for col, val in enumerate(voucher_headers):
            voucher_ws.write(0, col, val, header_fmt)
        voucher_moves = self.env['account.move'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'posted'),
            ('move_type', 'not in', ['out_invoice', 'in_invoice'])
        ])
        row = 1
        for move in voucher_moves:
            for line in move.line_ids.filtered('tax_ids'):
                for tax in line.tax_ids:
                    tax_line = move.line_ids.filtered(lambda x: x.tax_line_id == tax)
                    vat_amount = sum(tl.balance for tl in tax_line)
                    voucher_ws.write(row, 0, str(move.date), text_fmt)
                    voucher_ws.write(row, 1, move.name or '', text_fmt)
                    voucher_ws.write(row, 2, move.partner_id.name or '', text_fmt)
                    voucher_ws.write(row, 3, move.move_type, text_fmt)
                    voucher_ws.write(row, 4, tax.name, text_fmt)
                    voucher_ws.write(row, 5, line.tax_base_amount, curr_fmt)
                    voucher_ws.write(row, 6, vat_amount, curr_fmt)
                    row += 1

        # Remove placeholder sheets if present (avoid duplicate sheet names)
        # (No action needed since we now create and fill them above)

        workbook.close()
        output.seek(0)
        data = output.read()
        self.excel_file     = base64.b64encode(data)
        self.excel_filename = 'VAT201_Report_%s.xlsx' % self.date_from

        return {
            'type': 'ir.actions.act_url',
            'url': (
                '/web/content/?model=%(m)s&id=%(id)d&'
                'field=excel_file&filename=%(fn)s&download=true'
            ) % {
                'm': self._name,
                'id': self.id,
                'fn': self.excel_filename,
            },
            'target': 'new',
        }

    def print_report(self):
        # Dummy method to allow the Print PDF button to exist (no-op or raise NotImplementedError)
        raise NotImplementedError('PDF report is not implemented. Please use Export Excel.')

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
