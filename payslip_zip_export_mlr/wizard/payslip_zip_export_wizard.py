from odoo import models, api
import io
import zipfile
import base64

class PayslipZipExport(models.TransientModel):
    _name = 'payslip.zip.export'
    _description = 'Export Multiple Payslips as ZIP'

    @api.model
    def export_zip(self, payslip_ids):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            for payslip in self.env['hr.payslip'].browse(payslip_ids):
                pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
                    'om_hr_payroll.report_payslip_details',
                    [payslip.id]
                )
                filename = f"{payslip.employee_id.name.replace(' ', '_')}_Payslip_{payslip.date_to}.pdf"
                zip_file.writestr(filename, pdf_content)

        buffer.seek(0)
        zip_data = buffer.read()

        attachment = self.env['ir.attachment'].create({
            'name': 'Payslips.zip',
            'type': 'binary',
            'datas': base64.b64encode(zip_data),
            'res_model': 'payslip.zip.export',
            'res_id': self.id,
            'mimetype': 'application/zip',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
