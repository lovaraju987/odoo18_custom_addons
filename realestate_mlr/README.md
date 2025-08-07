# Real Estate Management Module for Odoo 18.0

## Overview
This module provides a comprehensive solution for real estate companies to manage properties, projects, reservations, ownership, rentals, payments, and furniture. Inspired by the features of the `nthub_realestate` module, it is designed for Odoo 18.0 and supports both English and Arabic languages.

---

## Key Features

- **Multi-language Support:** English and Arabic user interface.
- **Modern Dashboard:** Visual statistics for rented and sold units.
- **Region & Project Management:**
  - Define regions and group projects by region.
  - Create multiple projects and assign properties to them.
- **Property & Unit Management:**
  - Support for buildings, villas, and lands.
  - Auto-create sub-units (apartments, floors, etc.).
  - Customizable unit details and advanced data for marketing.
- **Furniture Management:**
  - Track furniture per unit.
  - Move furniture between company warehouse, units, and customer warehouse.
- **Reservation System:**
  - Reserve units with a validity period and auto-cancel expired reservations.
  - Refund or transfer reservation value to customer account.
- **Ownership & Rental Systems:**
  - **Ownership:** Multiple installment plans, advance payments, extras (garage, club, maintenance), penalties for late payment.
  - **Rental:** Multiple rental periods (daily, weekly, monthly, yearly), insurance, contract renewal, annual rent increase.
- **Contract Management:**
  - Create and manage ownership and rental contracts.
  - Attach documents to contracts and print contract reports.
- **Installment & Payment Tracking:**
  - Generate accounting invoices for all payments.
  - Track payment status and generate reports/statistics.
  - Print receipts and invoices for installment payments.
- **Settings:**
  - Reservation validity days, furniture transfer options, income and commission accounts.

---

## Data Models

- `realestate.region`: Manage regions for projects.
- `realestate.project`: Manage real estate projects.
- `realestate.property`: Manage properties under projects.
- `realestate.unit`: Manage sub-units of properties.
- `realestate.furniture`: Track and transfer furniture.
- `realestate.reservation`: Handle unit reservations.
- `realestate.ownership_contract`: Manage ownership contracts and installments.
- `realestate.rental_contract`: Manage rental contracts and payments.
- `realestate.installment_plan`: Define installment templates and penalties.
- `realestate.payment`: Track all payments and receipts.
- `realestate.settings`: Module configuration and options.

---

## Menus & Views

- Dashboard
- Regions
- Projects
- Properties/Units
- Furniture
- Reservations
- Ownership Contracts
- Rental Contracts
- Payments/Installments
- Reports (Receipts, Contracts, Statistics)
- Settings

---

## Integrations

- **Accounting:** For invoices, payments, and account management.
- **Inventory:** For furniture and warehouse management.
- **Document Management:** For contract attachments and document storage.

---

## Security & Access Rights

- User roles: Admin, Sales, Accountant, Property Manager, etc.
- Access rights for each model and menu.

---

## Optional Features

- Commission management (as an add-on)
- Customer portal for contract/payment tracking
- Automated notifications for reservations, payments, and contract renewals

---

## Development Roadmap

1. **Requirements & Data Model Design**
2. **Module Scaffolding**
3. **Model Implementation**
4. **Views & Menus**
5. **Business Logic (Reservations, Contracts, Payments)**
6. **Integrations (Accounting, Inventory)**
7. **Reports & Printouts**
8. **Access Rights & Security**
9. **Testing & QA**
10. **Documentation**

---

## License
LGPL-3

## Author
Your Company Name

## Support
For support, contact: [your-email@example.com](mailto:your-email@example.com)
