# Odoo Rental Sales

[![License: AGPL-3](https://img.shields.io/badge/license-AGPL--3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0-standalone.html)
[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://github.com/odoo/odoo/tree/18.0)

## Overview

The **Odoo Rental Sales** module is a comprehensive solution for businesses that need to manage rental operations within their Odoo system. This module enables companies to create and manage rental orders, track rental product availability, execute rental contracts, and handle rental-specific invoicing processes.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Setting Up Rental Products](#setting-up-rental-products)
  - [Creating Rental Orders](#creating-rental-orders)
  - [Managing Rental Contracts](#managing-rental-contracts)
  - [Contract Renewal](#contract-renewal)
- [Module Structure](#module-structure)
- [Technical Details](#technical-details)
- [Security](#security)
- [Changelog](#changelog)
- [Support](#support)
- [License](#license)

## Features

### Core Functionality
- **Rental Product Management**: Mark products as rental items with specific categories and agreements
- **Rental Order Processing**: Create and manage sales orders specifically for rental products
- **Contract Management**: Automated rental contract creation and lifecycle management
- **Contract Renewal**: Easy renewal process for existing rental contracts
- **Security Deposits**: Manage security amounts for rental products
- **Date Validation**: Built-in validation for rental start and end dates
- **Status Tracking**: Track rental contract status (New, Confirmed, Expired, Cancelled)

### Product Features
- **Rental Product Categories**: Organize rental products into specific categories
- **Product Agreements**: Attach rental agreements and terms to products
- **Security Amount Configuration**: Set security deposits for rental items
- **Unit of Measure Support**: Full UoM integration for rental quantities

### Contract Management
- **Automated Contract Creation**: Contracts are automatically generated when rental orders are confirmed
- **Contract Status Workflow**: New → Confirmed → Expired/Cancelled states
- **Contract Expiration Monitoring**: Automatic detection and marking of expired contracts
- **Reference Number Generation**: Unique reference numbers for contracts and order lines

### Integration Features
- **Sales Order Integration**: Seamless integration with Odoo's sales module
- **Partner Management**: Full customer relationship management
- **Currency Support**: Multi-currency support for international rentals
- **Portal Integration**: Customer portal access for rental information
- **Mail Integration**: Activity tracking and communication features

## Installation

### Prerequisites
- Odoo 18.0
- Required modules: `product`, `sale_management`, `base`

### Installation Steps
1. Download or clone the module to your Odoo addons directory
2. Update the app list in Odoo
3. Install the "Odoo Rental Sales" module from the Apps menu

### Dependencies
The module depends on the following Odoo core modules:
- `product` - Product management
- `sale_management` - Sales order functionality
- `base` - Core Odoo functionality

## Configuration

### Initial Setup

1. **Access Rights Configuration**
   - Navigate to Settings → Users & Companies → Groups
   - Assign users to "Rental Sales Manager" or "Rental Sales User" groups

2. **Sequence Configuration**
   - The module automatically creates sequences for:
     - Rental Order Lines (prefix: RO)
     - Rental Contracts (prefix: ROC)

3. **Menu Structure**
   After installation, you'll find the following menu structure:
   ```
   Rental
   ├── Sales
   │   ├── Rental Orders
   │   └── Rental Contracts
   ├── Products
   │   └── Rental Products
   └── Configuration
       ├── Rental Categories
       ├── Product Agreements
       └── Settings
   ```

### Product Configuration

1. **Enable Rental on Products**
   - Go to Products → Products
   - Open a product and check the "Rental" checkbox
   - Set the rental category and product agreement
   - Configure security amount if needed

2. **Rental Categories**
   - Navigate to Rental → Configuration → Rental Categories
   - Create categories to organize your rental products

3. **Product Agreements**
   - Go to Rental → Configuration → Product Agreements
   - Create rental agreements with terms and conditions
   - Upload agreement files if needed

## Usage

### Setting Up Rental Products

1. **Create a Rental Product**
   ```
   Products → Products → Create
   - Set product name and details
   - Check "Rental" checkbox
   - Select appropriate rental category
   - Assign product agreement
   - Set security amount
   - Configure unit price
   ```

2. **Rental Categories**
   - Create logical groupings for rental products
   - Examples: "Electronics", "Furniture", "Vehicles", "Equipment"

3. **Product Agreements**
   - Define rental terms and conditions
   - Upload legal agreement documents
   - Set sequence for agreement precedence

### Creating Rental Orders

1. **Standard Sales Order Process**
   ```
   Sales → Orders → Quotations → Create
   - Select customer
   - Add rental products using "Add Rental Product" wizard
   - Set quantities and prices
   - Confirm the order
   ```

2. **Rental Product Wizard**
   - Use the "Add Rental Product" button in sales orders
   - Select from available rental products
   - Set quantity and pricing
   - Product is automatically added to order line

### Managing Rental Contracts

1. **Automatic Contract Creation**
   - Contracts are automatically created when rental orders are confirmed
   - Each rental order line generates a corresponding contract
   - Contract inherits customer, product, and pricing information

2. **Contract Lifecycle**
   ```
   New → Confirmed → Expired/Cancelled
   ```

3. **Contract Actions**
   - **Confirm Contract**: Activate the rental agreement
   - **Reset to Draft**: Return contract to new status
   - **Cancel Contract**: Terminate the rental agreement

4. **Contract Monitoring**
   - System automatically checks for expired contracts
   - Contracts past their end date are marked as "Expired"
   - Cron job runs regularly to update contract statuses

### Contract Renewal

1. **Renewal Process**
   ```
   Rental Orders → Select Order Line → "Renew Contract"
   - Creates new contract based on existing terms
   - Allows modification of dates and terms
   - Maintains history of all contracts
   ```

2. **Renewal Features**
   - Pre-populated with existing contract data
   - Flexible date adjustment
   - Maintains relationship between contracts
   - Tracks renewal history

## Module Structure

### Models

#### Core Models
- **`rental.order.contract`**: Main contract management model
- **`rental.product.category`**: Product categorization
- **`rental.product.agreement`**: Rental agreement templates

#### Extended Models
- **`product.product`**: Extended with rental-specific fields
- **`sale.order`**: Enhanced for rental order processing
- **`sale.order.line`**: Extended with rental contract tracking

#### Wizard Models
- **`rental.product`**: Wizard for adding rental products to orders

### Data Files
- **Sequences**: Automatic numbering for contracts and order lines
- **Security**: Access rights and group definitions
- **Menus**: Navigation structure for rental functionality

### Views
- **Form Views**: Detailed forms for all rental entities
- **Tree Views**: List views for efficient data browsing
- **Search Views**: Advanced filtering and searching
- **Wizard Views**: Guided workflows for common tasks

## Technical Details

### Database Schema

#### Key Fields

**rental.order.contract**
- `reference_no`: Unique contract identifier
- `partner_id`: Customer reference
- `product_id`: Rental product
- `qty`: Rental quantity
- `unit_price`: Rental rate
- `date_start`: Contract start date
- `date_end`: Contract end date
- `contract_status`: Contract state

**product.product** (Extended)
- `rental`: Boolean flag for rental products
- `category_id`: Rental category assignment
- `product_agreement_id`: Associated agreement
- `security_amount`: Required security deposit

### Business Logic

#### Contract Creation Workflow
1. Customer creates sales order with rental products
2. Order confirmation triggers contract creation
3. Contract inherits all relevant order information
4. Contract status begins as "New"
5. Manual confirmation activates the contract

#### Expiration Management
- Automated cron job checks contract end dates
- Expired contracts are automatically flagged
- Status changes are tracked for audit purposes

#### Validation Rules
- End date must be after start date
- Rental products can only be added to rental orders
- Contract modifications require appropriate permissions

### API Methods

#### Key Methods

**rental.order.contract**
- `action_confirm_contract()`: Confirm contract
- `action_reset_contract()`: Reset to draft
- `action_cancel_contract()`: Cancel contract
- `_contract_expiration()`: Check for expired contracts

**sale.order.line**
- `action_renew_contract()`: Initiate contract renewal
- `_compute_current_contract_values()`: Update contract references

## Security

### Access Groups
- **Rental Sales Manager**: Full access to all rental functions
- **Rental Sales User**: Standard user access with limited administrative functions

### Permissions Matrix
| Model | Manager | User |
|-------|---------|------|
| Rental Contracts | CRUD | CRU |
| Rental Categories | CRUD | R |
| Product Agreements | CRUD | R |
| Rental Products | CRUD | CRU |

### Security Features
- Record-level security rules
- Company-based data separation
- User group-based access control
- Audit trail for all contract changes

## Troubleshooting

### Common Issues

1. **Contract Not Created**
   - Ensure product is marked as rental
   - Verify order confirmation completed
   - Check user permissions

2. **Date Validation Errors**
   - Ensure end date is after start date
   - Verify date format compatibility
   - Check timezone settings

3. **Missing Rental Products**
   - Confirm rental checkbox is enabled
   - Verify product category assignment
   - Check product access rights

### Debug Mode
Enable developer mode to access additional debugging information and technical views.

## Changelog

### Version 18.0.1.0.0 (2025-02-19)
- Initial release for Odoo 18.0
- Core rental management functionality
- Integration with sales module
- Contract lifecycle management
- Automated contract renewal
- Security and access control implementation

## Roadmap

### Planned Features
- Invoice integration for rental billing
- Advanced pricing models (daily, weekly, monthly rates)
- Inventory tracking for rental products
- Maintenance scheduling
- Customer portal enhancements
- Reporting and analytics dashboard

## Support

### Developer Information
- **Company**: [Cybrosys Techno Solutions](https://cybrosys.com/)
- **Version 16 Developer**: Aswathi PN
- **Version 17 Developer**: JANISH BABU EK  
- **Version 18 Developer**: Afthab K Naufal
- **Contact**: odoo@cybrosys.com

### Documentation
- **Odoo Documentation**: [Official Odoo Docs](https://www.odoo.com/documentation/18.0/)
- **Installation Guide**: [Setup Instructions](https://www.odoo.com/documentation/18.0/setup/install.html)

### Community
- Report issues and feature requests through the appropriate channels
- Contribute to module improvement through code reviews
- Share feedback and suggestions for enhancement

## License

This module is licensed under the GNU Affero General Public License v3.0 (AGPL-3).

```
Odoo Rental Sales
Copyright (C) 2025-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
```

---

**© 2025 Cybrosys Techno Solutions. All rights reserved.**
