{
    "name": "VAT Return Report (MLR)",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Custom VAT return report for Odoo 18",
    "author": "Your Company",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/vat_report_views.xml",
        "report/vat_report_template.xml"
    ],
    "installable": True,
    "application": False,
    "post_init_hook": "post_init_hook"
}
