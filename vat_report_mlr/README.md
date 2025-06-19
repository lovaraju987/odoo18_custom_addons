# VAT Return Report (MLR) for Odoo 18

## Overview
This module provides a UAE VAT-201 compliant reporting solution for Odoo 18, enabling users to generate, review, and export VAT-201 reports in Excel format. The report structure and output closely follow the UAE Federal Tax Authority (FTA) requirements and are inspired by the Stranbys VAT-201 module.

---

## Features

- **UAE VAT-201 Compliance:** Generates Excel reports in the official FTA VAT-201 format, suitable for submission.
- **Detailed Excel Export:** Download VAT-201 reports as Excel files, including all required sections and detailed transaction tabs.
- **Sales, Purchase, and Other Voucher Tabs:** Each report includes:
  - **VAT 201- VAT Return:** Summary sheet with company details, period, sales and purchase VAT breakdown, and summary calculations.
  - **Sales:** Line-by-line details of all sales invoices in the selected period, including date, invoice number, customer, tax, base amount, and VAT amount.
  - **Purchase:** Line-by-line details of all purchase bills in the selected period, including date, bill number, vendor, tax, base amount, and VAT amount.
  - **Other Voucher:** Details of other posted accounting entries with VAT impact (e.g., miscellaneous journals), including date, entry, partner, type, tax, base amount, and VAT amount.
- **Custom Date Range:** Select any reporting period using a wizard interface.
- **Company Info:** Automatically includes company name, TRN, and reporting period in the report header.
- **Menu Integration:** Access the report from Accounting > Reporting > UAE VAT-201.
- **Access Rights:** Secure access to the report wizard and export functionality.

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
4. Open the Excel file to review the summary and detailed transaction tabs.
5. (Optional) The Print PDF button is present for future use but is not implemented in this version.

---

## Report Format

- **VAT 201- VAT Return (Main Sheet):**
  - Header: Company name, TRN, reporting period, tax year.
  - VAT on Sales and All Other Outputs: Line-by-line and total VAT on sales.
  - VAT on Expenses and All Other Inputs: Line-by-line and total VAT on purchases.
  - Summary: Net VAT due, total due tax, total recoverable tax, payable tax.
  - Footer: Report generation timestamp.
- **Sales Tab:** Date, Invoice, Customer, Tax, Base Amount (AED), VAT Amount (AED).
- **Purchase Tab:** Date, Bill, Vendor, Tax, Base Amount (AED), VAT Amount (AED).
- **Other Voucher Tab:** Date, Entry, Partner, Type, Tax, Base Amount (AED), VAT Amount (AED).

---

## Technical Details

- **Odoo Version:** 18.0
- **Dependencies:** `account`, `mail`
- **Excel Library:** Uses `xlsxwriter` (included in Odoo 18)
- **Model:** `vat.return.report` (transient model for the wizard)
- **Security:** Access rights are defined for the wizard.
- **No server-side PDF:** The Print PDF button is a placeholder; only Excel export is implemented.

---

## Customization & Extension

- The report structure can be extended for other GCC VAT formats.
- Tax codes and sections can be made configurable for future needs.
- Additional columns or filters can be added to the detailed tabs as required.

---

## Support

For questions or support, please contact your Odoo administrator or the module author.

---

## License

AGPL-3
