Here is a detailed `README.md` for your **API Management Base** Odoo module:

---

# API Management Base (Odoo 18)

**Version:** 18.0
**Author:** Lovaraju
**License:** LGPL-3
**Category:** Technical
**Maintainer:** Lovaraju

## 📦 Summary

The **API Management Base** is a reusable Odoo 18 module that provides a foundational system to manage API access through API keys, define dynamic endpoints, and log API usage. This module is ideal for developers and businesses aiming to expose controlled data via secure APIs from Odoo.

---

## 🔧 Features

* ✅ API Key Management (creation, regeneration, deactivation)
* ✅ Dynamic API Endpoint definition from backend UI
* ✅ API Access Logs with request tracking
* ✅ Dashboard to monitor API usage and status
* ✅ Wizard for API key generation
* ✅ Secured access with token validation
* ✅ Fully backend managed — no code changes needed to add new endpoints

---

## 🧩 Dependencies

* `base` (Odoo Core)

---

## 📁 Module Structure

```bash
api_management/
├── controllers/
│   ├── __init__.py
│   ├── controllers.py              # Base API endpoints (REST)
│   ├── dynamic.py                  # Logic for dynamic endpoint access
├── models/
│   ├── __init__.py
│   ├── api_access_log.py          # Logs API access attempts and metadata
│   ├── res_api_key.py             # Model for storing API keys
│   ├── res_api_endpoint.py        # Model for defining allowed API models/fields
│   ├── res_api_endpoint_wizard.py# Wizard to create API endpoint definitions
├── views/
│   ├── api_access_log_views.xml
│   ├── api_dashboard_views.xml
│   ├── res_api_key_views.xml
│   ├── res_api_endpoint_views.xml
│   ├── res_api_endpoint_wizard_views.xml
│   ├── templates.xml
├── security/
│   ├── ir.model.access.csv
├── __manifest__.py
└── __init__.py
```

---

## 🚀 Installation

1. Download or clone this repository into your Odoo `addons` directory.
2. Update the Odoo app list.
3. Install the **API Management Base** module via the Odoo Apps interface.

---

## ⚙️ Usage

### 1. Generate API Keys

* Navigate to **API Keys** menu.
* Create a new API Key record.
* Assign a user and expiry if needed.
* Key can be regenerated using the `Regenerate` button.

### 2. Define API Endpoints

* Use the **API Endpoint Wizard** to define:

  * Model (`res.partner`, `sale.order`, etc.)
  * Allowed fields
  * Optional domain and sorting
* The endpoint will be available at:

  ```
  /api/{model_name}
  ```

  secured by API Key.

### 3. Access Logs

* Every API call is logged with:

  * Timestamp
  * Endpoint
  * Success/Failure
  * Key used
  * Response time

### 4. Monitor via Dashboard

* Use the **API Dashboard** to see a real-time summary of:

  * Active Keys
  * Requests over time
  * Most used endpoints

---

## 🔐 Security

* Each request must include a valid `x-api-key` header.
* Unauthorized or expired keys are blocked.
* Logs help audit and analyze suspicious activity.

---

## 📘 Example API Request

```bash
GET /api/res.partner
Headers:
  x-api-key: your_generated_api_key
```

---

## 🧪 Future Enhancements

* ✅ Key-level rate limiting
* ✅ Per-endpoint permission roles
* ✅ Field-level security
* ✅ Custom response transformers

---

## 🤝 Contributing

Pull requests and enhancements are welcome. Please fork the repository and submit changes via GitHub or your internal Git system.

---
