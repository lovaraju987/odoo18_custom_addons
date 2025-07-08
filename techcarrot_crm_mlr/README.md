# TechCarrot CRM Customization Module

This Odoo 18 module extends the standard CRM module with additional custom fields to better track opportunities and leads.

## Features

### New Fields Added to CRM Leads/Opportunities:

1. **Point of Contact** (`point_of_contact_id`)
   - Type: Many2one to res.partner
   - Links to contact records (individuals only)
   - Auto-populated when a customer is selected
   - Domain restricted to non-company contacts

2. **Practice** (`practice`)
   - Type: Selection field
   - Options: Web Development, Mobile Development, Data Analytics, Cloud Services, AI/ML Solutions, Cybersecurity, IT Consulting, Other
   - Helps categorize opportunities by service offering

3. **Deal Manager** (`deal_manager_id`)
   - Type: Many2one to hr.employee
   - Links to employee records
   - Automatically updates the assigned user when changed
   - Displayed with employee avatar widget

4. **Proposal Submission Date** (`proposal_submission_date`)
   - Type: Date field
   - Tracks when proposals are submitted to customers
   - Useful for pipeline management and follow-ups

5. **Engaged Presales** (`engaged_presales`)
   - Type: Boolean (checkbox)
   - Indicates whether presales team is involved
   - Useful for resource planning and tracking

6. **Industry** (`industry`)
   - Type: Selection field
   - Comprehensive list of industry sectors
   - Options include: Automotive, Banking & Finance, Construction, Education, Energy & Utilities, Government, Healthcare, etc.

## Installation

1. Copy this module to your Odoo addons directory
2. Update the app list in Odoo
3. Install the "TechCarrot CRM Customization" module
4. The new fields will be available in the CRM module

## Usage

### Form View
- Custom fields are organized in a dedicated "TechCarrot Custom Fields" section
- Point of Contact appears near the Customer field for easy access
- Deal Manager appears near the Salesperson field

### List View
- All custom fields are available as optional columns
- Can be shown/hidden based on user preference

### Search and Filters
- Search by any custom field
- Group by Practice, Industry, Deal Manager, or Engaged Presales
- Quick filters for "Engaged Presales" and "Proposal Submitted"

### Kanban View
- Practice and Industry displayed as badges
- Presales engagement shown with special indicator

## Technical Details

- **Odoo Version**: 18.0
- **Dependencies**: crm, hr
- **Model Extended**: crm.lead
- **Author**: TechCarrot

## Automatic Behaviors

1. **Point of Contact Auto-Population**: When a customer is selected, the system automatically tries to set an appropriate contact person
2. **User Assignment**: When a Deal Manager is assigned, the system updates the responsible user if the employee has a linked user account

## Customization

The selection field options (Practice and Industry) can be easily modified in the `models/crm_lead.py` file to match your organization's specific needs.
