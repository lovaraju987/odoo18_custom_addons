# Real Estate Management Module (Phase 1)

## Overview
This Odoo 18.0 module provides a robust foundation for real estate management, supporting regions, projects, properties, and units, with enhanced data fields, dashboards, bulk unit creation, and granular access rights.

---

## Core Features
- **Region Management:**
  - Manage regions with name, code, location, manager, and description.
- **Project Management:**
  - Projects linked to regions, with location, start/end dates, status, and description.
- **Property Management:**
  - Properties linked to projects, with type (building, villa, land, commercial, office), address, price, number of rooms, amenities, image, notes, and description.
- **Unit Management:**
  - Units linked to properties, with name, floor, area, bedrooms, bathrooms, price, status (available, reserved, sold, rented), image, notes, and description.
- **Bulk Unit Creation Wizard:**
  - Wizard to auto-create multiple units for a property with configurable details.
- **Dashboard:**
  - Dashboard menu showing total, available, sold, and rented units.
- **Menus:**
  - All models accessible from a Real Estate root menu, with a dashboard and all management screens.
- **Access Rights:**
  - Three user groups: Manager (full access), Sales (no delete), Viewer (read-only), for all core models.

---

## Technical Details
- **Models:**
  - `realestate.region`, `realestate.project`, `realestate.property`, `realestate.unit`
- **Wizards:**
  - `realestate.dashboard` (dashboard stats)
  - `realestate.unit.create.wizard` (bulk unit creation)
- **Views:**
  - List and form views for all models, showing all key fields
  - Dashboard form view
  - Bulk unit creation wizard form
- **Security:**
  - Security groups and access rules for Manager, Sales, Viewer
- **Other:**
  - All fields and labels are translatable
  - Images supported for properties and units

---

## How to Use
1. **Set up regions, projects, properties, and units from the Real Estate menu.**
2. **Use the Dashboard menu to view unit statistics.**
3. **From a property, use the action menu to launch the Auto Create Units wizard for bulk unit creation.**
4. **Assign users to Manager, Sales, or Viewer groups for appropriate access.**

---

## Next Steps
- Add advanced marketing fields, reservation system, contract management, and further dashboards in future phases.

---

## Author
Your Company Name
