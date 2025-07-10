# Sign OCA - Digital Document Signing for Odoo CE

[![License: AGPL-3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![OCA/sign](https://img.shields.io/badge/github-OCA%2Fsign-lightgray.png?logo=github)](https://github.com/OCA/sign/tree/18.0/sign_oca)
[![Version](https://img.shields.io/badge/version-18.0.1.1.0-green)](https://github.com/OCA/sign)

## Overview

**Sign OCA** is a comprehensive digital document signing solution for Odoo Community Edition (CE). This module provides a complete signing workflow that allows users to create document templates, configure signature fields, manage signing roles, and handle the entire document signing process within Odoo.

Built using modern OWL (Odoo Web Library) framework, the module offers an intuitive interface for both backend users and portal signers, making it easy to handle digital signatures without requiring external services.

## Key Features

### 🎯 **Core Functionality**
- **Document Template Management**: Create and configure reusable PDF templates with signature fields
- **Multi-Signer Workflow**: Support for multiple signers with different roles and signing orders
- **Portal Integration**: External signers can sign documents through the portal without Odoo access
- **Role-Based Signing**: Define signing roles with automatic partner assignment rules
- **Real-time Tracking**: Monitor signature progress and document status
- **PDF Generation**: Automatic final PDF generation once all parties have signed

### 📋 **Template System**
- **Visual Field Configuration**: Right-click to add signature fields, text fields, and checkboxes on PDF pages
- **Auto-save Functionality**: Templates are automatically saved during configuration
- **Model Integration**: Link templates to specific Odoo models (partners, equipment, etc.)
- **Field Types Support**:
  - Text fields for data entry
  - Signature fields for digital signatures
  - Checkbox fields for confirmations
- **Template Reusability**: Create once, use multiple times across different records

### 👥 **Signing Roles & Partners**
- **Flexible Role System**: Define roles like "Customer", "Manager", "Equipment Operator"
- **Partner Assignment Policies**:
  - **Empty**: Manual partner assignment
  - **Default**: Use a predefined partner
  - **Expression**: Dynamic partner calculation using expressions (e.g., `${object.partner_id.id}`)
- **Commercial Partner Support**: Automatic handling of parent-child partner relationships

### 🔄 **Signing Workflows**
- **Template-based Signing**: Create signing requests directly from templates
- **Bulk Signing**: Generate multiple signing requests from list views
- **Sequential Signing**: Control signing order and dependencies
- **Portal Access**: Secure external access for signers via access tokens
- **Notification System**: Automatic email notifications and activity tracking

### 🔐 **Security & Access Control**
- **Granular Permissions**: Three user levels (User, Manager, Administrator)
- **Company Isolation**: Multi-company support with proper data isolation
- **Access Rules**: Secure access to own documents or all documents based on user role
- **Portal Security**: Token-based access for external signers

### 📱 **User Interface**
- **Modern OWL Components**: Built with Odoo's latest frontend framework
- **Responsive Design**: Works on desktop and mobile devices
- **Systray Integration**: Quick access to pending signatures via systray icon
- **Portal Interface**: Clean, user-friendly signing interface for external users

## Technical Architecture

### 🏗️ **Core Models**

#### Sign Template (`sign.oca.template`)
- Stores PDF templates and field configurations
- Manages template-to-model relationships
- Handles template versioning and activation

#### Sign Request (`sign.oca.request`)
- Central model for signing workflows
- Tracks document state and progress
- Manages final PDF generation
- Stores signing metadata and audit trail

#### Sign Request Signer (`sign.oca.request.signer`)
- Individual signer records within a request
- Tracks signature status and timestamps
- Stores signature data and positioning

#### Sign Role (`sign.oca.role`)
- Defines signing roles and partner assignment rules
- Supports dynamic partner calculation
- Used for automatic signer assignment

#### Sign Field (`sign.oca.field`)
- Defines available field types
- Configures default values and behaviors

### 🎨 **Frontend Components**

#### OWL Components
- **sign_oca_configure**: Template configuration interface
- **sign_oca_pdf**: PDF viewer and field editor
- **sign_oca_pdf_portal**: Portal signing interface
- **sign_oca_pdf_common**: Shared PDF functionality
- **sign_oca_preview**: Template preview component

#### JavaScript Services
- **systray_service**: Manages pending signature notifications
- **sign_oca**: Core signing functionality and API integration

### 🛡️ **Security Framework**

#### User Groups
1. **User: Own Documents Only** (`sign_oca_group_user`)
   - Access to own signing requests
   - Basic template usage
   
2. **Manager: All Documents** (`sign_oca_group_manager`)
   - Access to all signing requests
   - Advanced template management
   
3. **Administrator** (`sign_oca_group_admin`)
   - Full system configuration
   - Role and field type management

#### Record Rules
- Company-based data isolation
- User-based access restrictions
- Partner relationship respect

## Installation & Dependencies

### Requirements
- Odoo 18.0
- Python packages: PyPDF2, reportlab

### Dependencies
- `web_editor`: For rich text editing capabilities
- `portal`: For external user access
- `base_sparse_field`: For optimized field storage

### Installation Steps

1. **Download the module**:
   ```bash
   git clone https://github.com/OCA/sign.git
   cd sign
   ```

2. **Copy to addons directory**:
   ```bash
   cp -r sign_oca /path/to/your/odoo/addons/
   ```

3. **Update module list**:
   - Go to Apps → Update Apps List

4. **Install the module**:
   - Search for "Sign Oca"
   - Click Install

## Configuration Guide

### 1. Initial Setup

1. **Access the Sign module**:
   - Navigate to **Sign** in the main menu

2. **Configure user permissions**:
   - Go to **Settings → Users & Companies → Users**
   - Assign appropriate Sign groups to users

### 2. Creating Field Types

1. **Access Field Configuration**:
   - Go to **Sign → Settings → Field Types**

2. **Create field types**:
   ```
   Name: Customer Signature
   Type: Signature
   Default Value: (empty)
   
   Name: Date Field
   Type: Text
   Default Value: ${today}
   
   Name: Agreement Checkbox
   Type: Check
   Default Value: (empty)
   ```

### 3. Setting Up Roles

1. **Access Roles**:
   - Go to **Sign → Settings → Roles**

2. **Create signing roles**:
   ```
   Customer Role:
   - Name: Customer
   - Partner Selection: Expression
   - Expression: ${object.partner_id.id}
   
   Manager Role:
   - Name: Manager
   - Partner Selection: Default
   - Default Partner: [Select manager partner]
   ```

### 4. Creating Templates

1. **Create a new template**:
   - Go to **Sign → Templates**
   - Click **Create**
   - Fill in:
     - Name: "Service Agreement Template"
     - Upload PDF file
     - Link to Model: (optional, e.g., Project)

2. **Configure template fields**:
   - Click **Configure** button
   - Right-click on PDF to add fields
   - Configure each field:
     - Field Type
     - Role assignment
     - Required/Optional status
     - Default values

## Usage Instructions

### Creating and Managing Templates

#### Step 1: Template Creation
1. Navigate to **Sign → Templates**
2. Click **Create** and provide:
   - Template name
   - PDF document upload
   - Associated model (optional)
   - Location requirement settings

#### Step 2: Field Configuration
1. Click **Configure** on the template
2. Right-click on the PDF to add fields:
   - **Text Fields**: For data entry (names, dates, numbers)
   - **Signature Fields**: For digital signatures
   - **Checkboxes**: For confirmations and agreements
3. Configure each field:
   - Assign to specific roles
   - Set as required or optional
   - Configure default values
   - Position and size adjustment

#### Step 3: Role Assignment
- Link fields to predefined roles
- Roles determine which signer fills which fields
- Configure automatic partner assignment rules

### Signing Workflows

#### Method 1: Direct Template Signing
1. Go to **Sign → Templates**
2. Select a template and click **Sign**
3. Add signers manually or use role-based assignment
4. Link to specific records if template is model-bound
5. Send for signature

#### Method 2: Bulk Signing from List Views
1. Navigate to any model's list view (e.g., Contacts)
2. Select multiple records
3. Choose **Actions → Sign from Template**
4. Select appropriate template
5. Requests are created automatically

#### Method 3: Portal Signing
1. External signers receive email with signing link
2. Access document through secure portal
3. Fill required fields and sign
4. System automatically updates status

### Monitoring and Management

#### Tracking Signatures
- **Systray Icon**: Shows pending signature count
- **Request Dashboard**: Monitor all signing requests
- **Status Tracking**: Draft → Sent → Signed → Completed
- **Activity Feed**: Automatic logging of signing events

#### Document Management
- **Version Control**: Track document changes
- **Final PDF**: Generated automatically after all signatures
- **Audit Trail**: Complete history of signing process
- **Storage**: Secure document storage with access controls

## Advanced Features

### Dynamic Partner Assignment

Use expressions to automatically assign partners based on record data:

```python
# Customer from related field
${object.partner_id.id}

# Manager from company
${object.company_id.partner_id.id}

# Conditional assignment
${object.partner_id.id if object.state == 'confirmed' else object.user_id.partner_id.id}
```

### Model Integration

Link templates to specific models for automatic availability:

1. **Equipment Maintenance**:
   - Link template to `maintenance.equipment`
   - Automatic signing actions in equipment forms
   - Context-aware signer assignment

2. **Project Management**:
   - Link to `project.project`
   - Customer and project manager signing
   - Milestone-based document signing

3. **Sales Orders**:
   - Customer approval workflows
   - Terms and conditions acceptance
   - Order confirmation signatures

### Portal Customization

Templates support custom CSS and branding:

```css
/* Custom portal styling */
.o_portal_sign_document_body {
    background: #f8f9fa;
    font-family: 'Custom Font', sans-serif;
}

.o_sign_field_signature {
    border: 2px solid #007bff;
    border-radius: 8px;
}
```

### Webhook Integration

Extend functionality with custom webhooks:

```python
class SignOcaRequest(models.Model):
    _inherit = 'sign.oca.request'
    
    def _post_process_signed_request(self):
        super()._post_process_signed_request()
        # Custom webhook logic
        self._send_completion_webhook()
        
    def _send_completion_webhook(self):
        # Send notification to external systems
        pass
```

## API Reference

### Python API

#### Creating Requests Programmatically

```python
# Create signing request
request = self.env['sign.oca.request'].create({
    'name': 'Contract Signature',
    'template_id': template.id,
    'record_ref': f'{record._name},{record.id}',
    'signer_ids': [(0, 0, {
        'partner_id': partner.id,
        'role_id': role.id,
    })]
})

# Send for signature
request.send_sign_request()
```

#### Template Management

```python
# Create template
template = self.env['sign.oca.template'].create({
    'name': 'Service Agreement',
    'data': base64_pdf_data,
    'filename': 'agreement.pdf',
    'model_id': self.env.ref('base.model_res_partner').id,
})

# Add template items
template.item_ids.create({
    'template_id': template.id,
    'field_id': field.id,
    'role_id': role.id,
    'required': True,
    'page': 1,
    'posX': 100,
    'posY': 200,
    'width': 150,
    'height': 30,
})
```

### REST API Endpoints

#### Portal Access
- `GET /sign_oca/document/<signer_id>/<access_token>`: Access signing document
- `POST /sign_oca/sign/<signer_id>`: Submit signature data

#### Asset Management
- `GET /sign_oca/get_assets.css`: Get signing interface CSS
- `GET /sign_oca/get_assets.js`: Get signing interface JavaScript

## Testing

### Running Tests

```bash
# Run all sign_oca tests
odoo-bin -d test_db -i sign_oca --test-enable --stop-after-init

# Run specific test class
odoo-bin -d test_db --test-tags sign_oca.TestSign
```

### Test Coverage

The module includes comprehensive tests covering:

- **Template Management**: Creation, configuration, field management
- **Signing Workflows**: Complete signing processes
- **Portal Access**: External signer functionality
- **Security**: Access controls and permissions
- **Integration**: Model linking and bulk operations

### Example Test Case

```python
def test_complete_signing_workflow(self):
    """Test complete signing workflow"""
    # Create template with fields
    template = self._create_test_template()
    
    # Create signing request
    request = self._create_signing_request(template)
    
    # Sign document
    signer = request.signer_ids[0]
    self._sign_document(signer)
    
    # Verify completion
    self.assertEqual(request.state, 'signed')
    self.assertTrue(request.signed)
```

## Troubleshooting

### Common Issues

#### 1. PDF Not Loading
**Symptoms**: Template configuration screen is blank
**Solution**: 
- Verify PDF file is valid and not corrupted
- Check file size limits in Odoo configuration
- Ensure proper file permissions

#### 2. Signature Fields Not Saving
**Symptoms**: Fields disappear after configuration
**Solution**:
- Check user permissions (need Sign User group minimum)
- Verify JavaScript console for errors
- Clear browser cache and retry

#### 3. Portal Access Issues
**Symptoms**: External signers can't access documents
**Solution**:
- Verify access tokens are valid
- Check mail server configuration
- Ensure portal is enabled in Odoo settings

#### 4. Performance Issues
**Symptoms**: Slow template loading or signing
**Solution**:
- Optimize PDF file sizes
- Enable Odoo caching
- Check database performance

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
# In odoo.conf
log_level = debug
log_handler = :DEBUG

# Or set logger in code
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
```

### Support Channels

- **GitHub Issues**: [OCA/sign Issues](https://github.com/OCA/sign/issues)
- **OCA Community**: [Odoo Community Association](https://odoo-community.org)
- **Documentation**: [OCA Documentation](https://github.com/OCA/sign/wiki)

## Development

### Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** following OCA guidelines
4. **Add tests** for new functionality
5. **Submit pull request**

### Code Standards

- Follow OCA development guidelines
- Use proper Python docstrings
- Include comprehensive tests
- Follow Odoo coding standards
- Update documentation

### Module Extension

Create dependent modules for specific use cases:

```python
# __manifest__.py
{
    'name': 'Sign OCA Equipment',
    'depends': ['sign_oca', 'maintenance'],
    'auto_install': True,
}

# models/maintenance_equipment.py
class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    
    sign_request_ids = fields.One2many(
        'sign.oca.request', 
        compute='_compute_sign_requests'
    )
```

## Roadmap

### Current Development (v18.0.1.1.0)
- ✅ Core signing functionality
- ✅ Portal integration
- ✅ Multi-signer workflows
- ✅ Template management
- ✅ Role-based assignment

### Planned Features (v18.0.2.0.0)
- 🔄 Advanced signature verification
- 🔄 Certificate-based signing
- 🔄 OTP authentication for signers
- 🔄 Mobile app integration
- 🔄 Advanced reporting dashboard

### Future Enhancements
- 📋 Document versioning system
- 📋 Advanced workflow automation
- 📋 Integration with external signing services
- 📋 Blockchain signature verification
- 📋 AI-powered document analysis

## License & Credits

### License
This module is licensed under **AGPL-3.0** - see the [LICENSE](LICENSE) file for details.

### Authors & Contributors

**Authors:**
- [Dixmit](http://www.dixmit.com) - Original development
- [Odoo Community Association (OCA)](https://odoo-community.org) - Community maintenance

**Contributors:**
- Enric Tobella (Dixmit) - Core development
- Víctor Martínez (Tecnativa) - Enhancements
- Mohamed Alkobrosli (Kencove) - Features and fixes

**Maintainer:**
- [@etobella](https://github.com/etobella) - Current maintainer

### Acknowledgments

Special thanks to:
- The OCA community for continuous support
- Odoo SA for the excellent framework
- All contributors and testers

---

**📧 Need Help?** Contact the maintainers or create an issue on GitHub.

**🌟 Like this module?** Give it a star on [GitHub](https://github.com/OCA/sign) and consider contributing!

**🔗 More OCA Modules:** Explore our [complete module catalog](https://github.com/OCA).
