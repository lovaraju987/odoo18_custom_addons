# VAT Return Report (MLR) for Odoo 18

## Overview
This module provides a UAE VAT-201 compliant report for Odoo 18, allowing users to generate and export VAT-201 reports in Excel format. It is inspired by the Stranbys VAT-201 module and tailored for UAE tax regulations.

---

## Features
- **UAE VAT-201 Compliance:** Generates reports in the format required by the UAE FTA.
- **Excel Export:** Download VAT-201 reports as Excel files for easy submission and review.
- **Sales & Purchase Breakdown:** Detailed tables for both sales and purchase VAT, including base and tax amounts.
- **Custom Date Range:** Select any period for reporting using a wizard interface.
- **Company Info:** Includes company name, TRN, and reporting period in the report header.
- **Menu Integration:** Access the report from Accounting > Reporting > UAE VAT-201.

---

## Installation & Setup
1. Ensure the **Invoicing (account)** and **Discuss (mail)** modules are installed.
2. Add this module to your Odoo custom addons path.
3. Update the Apps list and install the module.
4. Access the report via **Accounting > Reporting > UAE VAT-201**.

---

## Usage
1. Open the UAE VAT-201 menu under Accounting > Reporting.
2. In the wizard, select the start and end dates for your VAT period.
3. Click **Export Excel** to download the VAT-201 report in Excel format.
4. (Optional) Click **Print PDF** for a PDF version (if enabled).

---

## Technical Details
- **Odoo Version:** 18.0
- **Dependencies:** `account`, `mail`
- **Excel Library:** Uses `xlsxwriter` (included in Odoo 18)
- **Model:** `vat.return.report` (transient model for the wizard)
- **Security:** Access rights are defined for the wizard.

---

## Report Format
- **Header:** Company name, TRN, reporting period
- **Sales Table:** Tax type, base amount, tax amount, totals
- **Purchases Table:** Tax type, base amount, tax amount, totals
- **(Optional) Adjustments:** Add sections as required by UAE FTA

---

## Customization & Extension
- The report structure can be extended for other GCC VAT formats.
- Tax codes and sections can be made configurable for future needs.

---

## Support
For questions or support, please contact your Odoo administrator or the module author.

---

## License
AGPL-3
