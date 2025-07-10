# Subscription Management Module for Odoo 18

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-green.svg)](https://github.com/odoo/odoo/tree/18.0)

A comprehensive subscription package management module specifically designed for Odoo 18 Community edition. This module enhances the subscription management capabilities within the Odoo platform, providing users with advanced features and functionalities for efficiently handling subscription packages.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Module Structure](#module-structure)
- [Technical Overview](#technical-overview)
- [Dependencies](#dependencies)
- [License](#license)
- [Support](#support)

## ✨ Features

### Core Subscription Management
- **Subscription Packages**: Create and manage subscription packages with detailed customer information
- **Subscription Plans**: Define flexible subscription plans with customizable renewal periods
- **Product Lines**: Add multiple products to subscription packages with quantity and pricing
- **Stage Management**: Track subscription lifecycle through customizable stages (Draft, In Progress, Closed)

### Advanced Features
- **Automated Invoicing**: Automatic invoice generation based on subscription plans
- **Renewal Management**: Automated renewal alerts and processing
- **Email Notifications**: Automated email alerts for subscription renewals
- **Kanban View**: Visual subscription management with drag-and-drop stage progression
- **Analytics & Reporting**: Comprehensive subscription analysis and reporting

### Subscription Plans
- **Flexible Renewal Periods**: Support for days, weeks, months, and years
- **Multiple Limit Options**: 
  - One-time subscriptions
  - Manual closure
  - Custom renewal limits
- **Invoice Modes**: Manual or automated draft invoice generation
- **Short Codes**: Automatic generation of plan identification codes

### Customer Integration
- **Partner Integration**: Seamless integration with Odoo's partner management
- **Invoice & Shipping Addresses**: Support for separate billing and shipping addresses
- **Customer Subscription History**: Track all customer subscriptions and their status

### Automated Processes
- **Cron Jobs**: Daily automated checks for subscription renewals and closures
- **Email Templates**: Pre-configured email templates for renewal notifications
- **Automatic Closure**: Auto-close subscriptions when renewal limits are exceeded
- **Sales Order Integration**: Direct integration with Odoo's sales module

## 🚀 Installation

### Prerequisites
- Odoo 18.0 Community Edition
- Python 3.8 or higher
- Required Odoo modules: `base`, `sale_management`

### Installation Steps

1. **Download the Module**
   ```bash
   git clone <repository-url>
   cd subscription_package
   ```

2. **Copy to Addons Directory**
   ```bash
   cp -r subscription_package /path/to/odoo/custom-addons/
   ```

3. **Update Module List**
   - Navigate to Apps > Update Apps List in Odoo
   - Or restart Odoo service

4. **Install the Module**
   - Go to Apps menu
   - Search for "Subscription Management"
   - Click Install

## ⚙️ Configuration

### Initial Setup

1. **Configure Subscription Stages**
   - Navigate to Subscriptions > Configuration > Subscription Stages
   - Create or modify stages as needed
   - Set appropriate categories: Draft, In Progress, Closed

2. **Set Up Subscription Plans**
   - Go to Subscriptions > Configuration > Subscription Plans
   - Create subscription plans with:
     - Renewal periods (days/weeks/months/years)
     - Limit choices (ones/manual/custom)
     - Invoice modes (manual/draft)

3. **Configure Products**
   - Mark products as subscription products
   - Assign subscription plans to products
   - Set appropriate pricing

4. **Email Templates**
   - Review and customize renewal notification emails
   - Configure SMTP settings for automated emails

### Cron Job Configuration

The module includes an automated cron job that runs daily to:
- Check renewal dates
- Send renewal notifications
- Generate invoices
- Close expired subscriptions

To modify the cron schedule:
1. Go to Settings > Technical > Automation > Scheduled Actions
2. Find "Check Close Limit"
3. Adjust the interval as needed

## 📖 Usage

### Creating Subscription Packages

1. **Navigate to Subscriptions**
   - Go to Subscriptions > Subscription Packages
   - Click "Create"

2. **Fill Package Details**
   - Select customer
   - Choose subscription plan
   - Add product lines
   - Set start date

3. **Manage Subscription Lifecycle**
   - Start subscription (moves to "In Progress")
   - Generate sale orders
   - Track invoices
   - Close when needed

### Subscription Plans Management

1. **Create New Plan**
   - Go to Subscriptions > Configuration > Subscription Plans
   - Define renewal periods and limits
   - Set invoice generation mode

2. **Plan Features**
   - **Renewal Period**: Set how often subscriptions renew
   - **Limit Choice**: Control subscription duration
   - **Invoice Mode**: Choose manual or automatic invoicing

### Customer Subscription Tracking

- View all customer subscriptions from partner form
- Track subscription status and history
- Monitor upcoming renewals
- Manage subscription products

### Analytics and Reporting

1. **Subscription Analysis**
   - Navigate to Subscriptions > Reporting > Subscription Analysis
   - View subscription performance metrics
   - Filter by salesperson, plan, or date range

2. **Invoice Tracking**
   - Monitor subscription-related invoices
   - Track payment status
   - Generate revenue reports

## 🏗️ Module Structure

```
subscription_package/
├── __init__.py
├── __manifest__.py
├── README.md
├── data/
│   ├── ir_cron_data.xml              # Automated cron jobs
│   ├── ir_sequence.xml               # Sequence configurations
│   ├── mail_subscription_renew_data.xml  # Email templates
│   ├── subscription_package_stop_data.xml  # Close reasons
│   ├── subscription_stage_data.xml   # Default stages
│   └── uom_demo_data.xml             # Demo units of measure
├── doc/
│   └── RELEASE_NOTES.md              # Version history
├── models/
│   ├── __init__.py
│   ├── account_move.py               # Invoice extensions
│   ├── product_template.py          # Product extensions
│   ├── recurrence_period.py         # Recurrence periods
│   ├── res_partner.py               # Partner extensions
│   ├── sale_order.py                # Sales order integration
│   ├── sale_order_line.py           # Sales line extensions
│   ├── subscription_package.py      # Main subscription model
│   ├── subscription_package_plan.py # Subscription plans
│   ├── subscription_package_product_line.py  # Product lines
│   ├── subscription_package_stage.py # Subscription stages
│   └── subscription_package_stop.py # Close reasons
├── report/
│   ├── __init__.py
│   ├── subscription_report.py       # Analytics model
│   └── subscription_report_view.xml # Report views
├── security/
│   ├── ir.model.access.csv          # Access rights
│   └── subscription_package_groups.xml  # User groups
├── static/
│   └── description/                 # Module description assets
├── views/
│   ├── *.xml                        # All view definitions
└── wizard/
    ├── __init__.py
    ├── subscription_close.py        # Closure wizard
    └── subscription_close_views.xml # Wizard views
```

## 🔧 Technical Overview

### Core Models

#### SubscriptionPackage (`subscription.package`)
Main model for managing subscription packages with features:
- Customer and plan association
- Product line management
- Stage-based workflow
- Automated invoice generation
- Renewal tracking

#### SubscriptionPackagePlan (`subscription.package.plan`)
Defines subscription plan templates:
- Flexible renewal periods
- Multiple limit options
- Invoice generation modes
- Plan analytics

#### SubscriptionPackageProductLine (`subscription.package.product.line`)
Manages products within subscriptions:
- Product selection
- Quantity and pricing
- Tax calculations
- Discount support

### Key Features Implementation

#### Automated Renewals
- Cron job checks daily for renewal dates
- Automatic email notifications
- Invoice generation based on plan settings
- Subscription closure for exceeded limits

#### Stage Management
- Kanban-based workflow
- Customizable stages
- Progress tracking
- Automated stage transitions

#### Integration Points
- Sales Orders: Seamless integration with Odoo sales
- Invoicing: Automated invoice generation
- Partners: Customer subscription tracking
- Products: Subscription product marking

### Security & Access Rights

The module implements role-based access control:
- Base user access for all subscription operations
- Proper model access rights
- Secure wizard operations
- User group management

## 📦 Dependencies

### Required Modules
- `base`: Odoo core functionality
- `sale_management`: Sales order management

### Python Dependencies
- `dateutil`: Date calculations for renewals
- Standard Odoo framework libraries

## 📄 License

This module is licensed under the GNU Affero General Public License v3.0 (AGPL v3).

You can modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3), Version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.

## 🏢 About Cybrosys Technologies

**Developer**: Cybrosys Technologies Pvt. Ltd.  
**Author**: SREERAG PM  
**Website**: [https://www.cybrosys.com](https://www.cybrosys.com)  
**Email**: [Contact Us](https://www.cybrosys.com/contact/)

### Company Information
- **Maintainer**: Cybrosys Techno Solutions
- **Support**: Professional Odoo implementation and support services
- **Expertise**: Custom Odoo development, module creation, and business solutions

## 🎯 Support & Contribution

### Getting Help
- **Documentation**: Refer to this README and inline code documentation
- **Community**: Join Odoo community forums
- **Professional Support**: Contact Cybrosys Technologies for enterprise support

### Bug Reports & Feature Requests
When reporting issues or requesting features, please include:
- Odoo version and edition
- Module version
- Detailed description of the issue/request
- Steps to reproduce (for bugs)
- Screenshots if applicable

### Contributing
We welcome contributions to improve this module:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📊 Version History

- **v18.0.1.0.0** (February 19, 2025)
  - Initial release for Odoo 18
  - Complete subscription management functionality
  - Automated renewal and invoicing
  - Kanban stage management
  - Analytics and reporting

## 🚀 Future Enhancements

Planned features for future versions:
- Advanced pricing rules
- Multi-currency support enhancements  
- Customer portal integration
- Advanced analytics dashboard
- API endpoints for external integration
- Mobile app compatibility

---

*This module is part of the Cybrosys Technologies Odoo addon collection. For more modules and Odoo services, visit [www.cybrosys.com](https://www.cybrosys.com)*
