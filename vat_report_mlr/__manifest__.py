{
    "name": "VAT Return Report (MLR)",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Custom UAE VAT-201 Excel report for Odoo 18",
    "description": """
        This module provides a custom VAT return report for the UAE, formatted as an Excel file.
        It is designed to meet the requirements of the UAE Federal Tax Authority (FTA) for VAT reporting.
    """,
    "website": "https://github.com/lovaraju987",
    "maintainers": ["lovaraju mylapalli"],
    "images": ["static/description/banner.png"],  
    "author": "Lovaraju Mylapalli",
    "depends": [
        "account",
        "mail"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/vat_report_views.xml",
        "report/vat_report_template.xml"
    ],
    "installable": True,
    "application": False,
    "post_init_hook": "post_init_hook"
}
