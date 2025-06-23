# Custom Odoo Modules: Technical & Functional Overview

This document provides a detailed overview of the custom Odoo modules developed in this repository. Each section covers the module's purpose, the business problem it solves, the technical approach, and key talking points for interviews or documentation.

---

## 1. api_management

**Purpose:**
A flexible, secure API management system for Odoo, enabling dynamic creation of RESTful endpoints, API key management, and access logging.

**Business Problem:**
Odoo's native API is not user-friendly for external integrations and lacks fine-grained access control, monitoring, and key management.

**Solution & Approach:**
- Backend UI for admins to generate/manage API keys and define endpoints.
- Dynamic endpoint creation for any Odoo model, with field-level access control.
- Logging for every API request (timestamp, endpoint, key, status).
- Dashboard for monitoring API usage and key status.

**Technical Details:**
- Models: `res_api_key`, `api_endpoint`, `api_access_log`.
- Controllers: RESTful endpoints with token validation.
- Security: Custom access rules, key expiry, per-endpoint permissions.
- Views: Wizards for endpoint/key creation, dashboards, and logs.
- Extensible for future features (rate limiting, transformers, etc.).

**Interview Talking Points:**
- Why dynamic endpoints? (No code needed for new APIs)
- How is security enforced? (x-api-key header, per-key/endpoint rules)
- How is logging/auditing handled?
- How to extend for new models or features?

---

## 2. employee_self_service_portal

**Purpose:**
A self-service portal for employees to manage their HR data (profile, attendance, payslips, leaves, expenses) without requiring paid user licenses.

**Business Problem:**
Odoo’s default portal is limited for HR self-service, and third-party solutions are often paid or not customizable.

**Solution & Approach:**
- Extended the portal to add `/my/employee` and submenus for HR features.
- Linked portal users to their `hr.employee` record.
- QWeb templates for profile, attendance, payslips, leaves, and expenses.
- Security rules for portal users to access only their own data.

**Technical Details:**
- Controllers: Custom routes for each HR feature.
- Models: Extensions to `hr.employee`, `hr.payslip`, `hr.attendance`, etc.
- Security: Record rules for portal users.
- Templates: Modular QWeb templates for each section.
- Optional: Notifications for missed check-ins, limited profile editing.

**Interview Talking Points:**
- How did you map portal users to employees?
- How did you ensure data privacy?
- How did you handle extensibility for new HR features?
- What challenges did you face with Odoo’s portal framework?

---

## 3. employee_shift_report

**Purpose:**
Generate detailed reports on employee shifts, including attendance, shift timings, and compliance with scheduled hours.

**Business Problem:**
Odoo’s standard reporting does not provide shift-level granularity or compliance checks for HR managers.

**Solution & Approach:**
- Wizard to select date ranges and employees.
- Aggregated attendance and shift data for reporting.
- Highlighted discrepancies (late check-in, early check-out, missed shifts).
- Export options (Excel/PDF).

**Technical Details:**
- Models: Transient model for report wizard.
- Data aggregation: Custom SQL or ORM queries for performance.
- Views: Wizard, report templates.
- Export: Used `xlsxwriter` for Excel, QWeb for PDF.

**Interview Talking Points:**
- How did you optimize reporting for large datasets?
- How did you handle time zone and localization?
- How did you ensure report accuracy and compliance logic?

---

## 4. payslip_zip_export_mlr

**Purpose:**
Allow HR managers to export multiple employee payslips as a single ZIP archive for easy distribution.

**Business Problem:**
Odoo only allows downloading payslips one by one, which is inefficient for payroll admins.

**Solution & Approach:**
- Wizard to select payslips by batch/date/employee.
- Generated individual PDF payslips and zipped them server-side.
- Provided a single download link for the ZIP file.

**Technical Details:**
- Models: Transient wizard for selection.
- PDF generation: Used Odoo’s report engine.
- ZIP creation: Used Python’s `zipfile` module.
- Security: Ensured only HR managers can access.

**Interview Talking Points:**
- How did you handle large ZIP files and memory usage?
- How did you ensure file naming and organization in the ZIP?
- How did you integrate with Odoo’s reporting engine?

---

## 5. portal_user_selector

**Purpose:**
Admin tool for selecting and managing portal users, for bulk operations or access management.

**Business Problem:**
Odoo’s default portal user management is limited and not user-friendly for bulk actions.

**Solution & Approach:**
- UI for searching, filtering, and selecting portal users.
- Enabled bulk actions (activate/deactivate, assign groups, etc.).
- Integrated with Odoo’s security and user models.

**Technical Details:**
- Models: Extensions to `res.users`.
- Views: Custom list/form views, mass action wizards.
- Security: Ensured only admins can use these tools.

**Interview Talking Points:**
- How did you handle performance for large user lists?
- How did you ensure safe bulk operations?
- How did you integrate with Odoo’s user/group system?

---

## 6. vat_report_mlr

**Purpose:**
Generate UAE VAT-201 compliant Excel reports for Odoo 18, matching FTA requirements.

**Business Problem:**
Odoo does not provide a UAE VAT-201 report out of the box, and existing solutions may not match local compliance needs.

**Solution & Approach:**
- Wizard for selecting date range and company.
- Aggregated sales, purchase, and other voucher data as per FTA format.
- Generated Excel files with summary and detailed tabs.
- Ensured compliance with FTA’s official template.

**Technical Details:**
- Models: Transient wizard, report logic.
- Data: Pulled from `account.move` and related models.
- Excel export: Used `xlsxwriter`.
- Security: Access rights for accounting users.

**Interview Talking Points:**
- How did you ensure compliance with FTA requirements?
- How did you structure the Excel output?
- How did you handle edge cases (multi-company, currency, etc.)?
- How would you extend for other GCC VAT formats?

---

# General Interview Preparation
- Be ready to discuss design decisions, security, extensibility, and Odoo-specific challenges.
- Mention performance optimizations, testing strategies, and documentation.
- If you contributed to OCA or followed their guidelines, highlight that as well.

