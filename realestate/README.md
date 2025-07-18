# Realestate Module

## Overview
The `realestate` module provides a foundational framework for managing real estate entities in Odoo. It introduces an abstract entity system, integrates with Odoo's partner/contact management, and is designed for extensibility by other real estate-related modules.

---

## Purpose
To offer a base structure for real estate management, supporting the creation and extension of real estate objects, and enabling integration with Odoo's core features.

---

## Key Features
- **Abstract Entity Model:**
  - `realestate.abstract.entity` inherits from `res.partner` and adds real estate-specific fields and logic.
  - Designed for further extension by estate, property, or asset modules.
- **Partner Integration:**
  - Overridden `res.partner` creation logic to support real estate entity creation based on the `type` field.
- **Communication Tracking:**
  - Integrates with Odoo's mail/thread for activity and communication logging.
- **User Interface:**
  - Tree, form, and kanban views for abstract entities.
  - Menus for navigation and management.
- **Security:**
  - Basic access rights and group definitions for real estate employees and managers.
- **Extensibility:**
  - Designed to be inherited by other modules (e.g., `realestate_estate`).

---

## Technical Details
### Models
- `realestate.abstract.entity`: Abstract model, inherits from `res.partner`, adds fields like `active`, `partner_id`, and a `type` selection.
- `res.partner`: Overridden to support creation of real estate entities based on the `type` field.

### Views
- Tree, form, and kanban views for abstract entities.
- Menus for navigation and management.

### Security
- Basic access rights and group definitions for real estate employees and managers.

---

## How It Works
- **Entity Creation:** Users can create new real estate entities, which are linked to partners and can be extended by other modules.
- **Integration:** Real estate entities are managed alongside contacts and other entities in Odoo.
- **Extensibility:** The abstract model can be inherited by modules like `realestate_estate` to add estate-specific logic.

---

## Example Use Cases
- Real estate agencies needing a base for property management.
- Companies planning to extend Odoo for real estate asset tracking.
- Integrations with CRM, sales, or rental modules for end-to-end property management.

---

## Credits
- **Author:** ACSONE SA/NV, Odoo Community Association (OCA)
- **Maintainers:** OCA, Denis Roussel

---

## Contribution & Support
- Issues and contributions are managed via the [OCA/vertical-realestate GitHub repository](https://github.com/OCA/vertical-realestate).
- Community support and documentation are available via OCA.
