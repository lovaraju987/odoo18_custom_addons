# Realestate Estate Module

## Overview
The `realestate_estate` module extends the Odoo real estate management system by introducing estate-specific models, property types, and business logic. It is designed to work with the base `realestate` module, providing a comprehensive solution for managing real estate properties, their classifications, and related business processes.

---

## Purpose
To enable Odoo users to manage real estate properties (estates) and their types, ensuring unique identification, classification, and integration with partner/contact management.

---

## Key Features
- **Estate Management:**
  - Model for real estate properties (`real.estate`), inheriting from the abstract entity in the base module.
  - Unique reference generation for each property.
  - Short and long descriptions for properties.
- **Property Type Management:**
  - Model for property types (`real.estate.type`) with unique code and name.
  - Enforces uniqueness of property type codes.
- **Integration:**
  - Links properties to types and partners.
  - Extends `res.partner` to support estate linkage.
- **User Interface:**
  - Form, list, kanban, and search views for estates and types.
  - Menus for easy navigation and management.
- **Security:**
  - Access rights for readers, employees, and managers.
  - Record rules to restrict access by company.
- **Demo Data:**
  - Example property types and demo estates for testing and demonstration.

---

## Technical Details
### Models
- `real.estate`: Inherits from `realestate.abstract.entity`, adds fields for type, reference, short/long description.
- `real.estate.type`: Stores property types, enforces unique codes.
- `res.partner`: Extended to add a new type for estate linkage.

### Views
- Form, list, kanban, and search views for both estates and types.
- Menus for estate and type management.

### Security
- Access rights for different user roles (reader, employee, manager).
- Record rules for company-based access control.

### Data
- Demo data and sequences for property references.

---

## How It Works
- **Property Creation:** Users can create new real estate properties, assign them a type, and provide detailed descriptions.
- **Type Management:** Admins can define new property types, each with a unique code and name.
- **Integration:** Properties are linked to partners and can be managed alongside contacts and other entities.
- **Security:** Only authorized users can create, edit, or delete properties and types, based on their assigned roles.

---

## Example Use Cases
- Real estate agencies managing a portfolio of properties.
- Companies tracking and classifying real estate assets.
- Integration with CRM, sales, or rental modules for end-to-end property management.

---

## Credits
- **Author:** ACSONE SA/NV, Odoo Community Association (OCA)
- **Maintainers:** OCA, Denis Roussel

---

## Contribution & Support
- Issues and contributions are managed via the [OCA/vertical-realestate GitHub repository](https://github.com/OCA/vertical-realestate).
- Community support and documentation are available via OCA.
