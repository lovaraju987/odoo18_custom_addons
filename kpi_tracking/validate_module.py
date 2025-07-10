#!/usr/bin/env python3
"""
KPI Tracking Module - Pre-Publication Validation Script
======================================================

This script validates the KPI Tracking module before publication on the Odoo App Store.

Author: OneTo7 Solutions
Website: https://www.oneto7solutions.in
Support: info@oneto7solutions.in
"""

import os
import sys
import json
import xml.etree.ElementTree as ET

MODULE_PATH = "c:\\odoo18_custom_addons\\kpi_tracking"

def validate_manifest():
    """Validate the __manifest__.py file"""
    print("🔍 Validating manifest file...")
    
    manifest_path = os.path.join(MODULE_PATH, "__manifest__.py")
    if not os.path.exists(manifest_path):
        print("❌ __manifest__.py not found!")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()
        
        # Basic validation
        required_fields = [
            'name', 'version', 'summary', 'description', 'author',
            'website', 'support', 'license', 'price', 'currency',
            'depends', 'data', 'demo', 'images'
        ]
        
        missing_fields = []
        for field in required_fields:
            if f'"{field}"' not in manifest_content:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False
        
        # Check license
        if '"license": "OPL-1"' not in manifest_content:
            print("❌ License should be OPL-1 for commercial modules")
            return False
        
        # Check price
        if '"price": 20.00' not in manifest_content:
            print("❌ Price should be set to $20.00")
            return False
        
        print("✅ Manifest validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Error validating manifest: {e}")
        return False

def validate_demo_data():
    """Validate demo data exists and is valid"""
    print("🔍 Validating demo data...")
    
    demo_path = os.path.join(MODULE_PATH, "demo", "demo_data.xml")
    if not os.path.exists(demo_path):
        print("❌ Demo data file not found!")
        return False
    
    try:
        tree = ET.parse(demo_path)
        root = tree.getroot()
        
        # Check for demo records
        records = root.findall(".//record")
        if len(records) < 5:
            print("❌ Insufficient demo data records")
            return False
        
        print(f"✅ Demo data validation passed ({len(records)} records)")
        return True
        
    except Exception as e:
        print(f"❌ Error validating demo data: {e}")
        return False

def validate_static_images():
    """Check for required static images"""
    print("🔍 Validating static images...")
    
    static_path = os.path.join(MODULE_PATH, "static", "description")
    if not os.path.exists(static_path):
        print("❌ Static description directory not found!")
        return False
    
    required_images = [
        "banner.png", "icon.png", "kpi_dashboard.png", 
        "kpi_form.png", "kpi_reports.png"
    ]
    
    missing_images = []
    for image in required_images:
        image_path = os.path.join(static_path, image)
        if not os.path.exists(image_path):
            missing_images.append(image)
    
    if missing_images:
        print(f"⚠️ Missing images: {', '.join(missing_images)}")
        print("   These need to be created before App Store submission")
        return False
    
    print("✅ Static images validation passed")
    return True

def validate_license():
    """Check for license file"""
    print("🔍 Validating license file...")
    
    license_path = os.path.join(MODULE_PATH, "LICENSE")
    if not os.path.exists(license_path):
        print("❌ LICENSE file not found!")
        return False
    
    print("✅ License file validation passed")
    return True

def validate_security():
    """Validate security files"""
    print("🔍 Validating security files...")
    
    security_path = os.path.join(MODULE_PATH, "security")
    required_files = [
        "security.xml", "kpi_tracking_rules.xml", "ir.model.access.csv"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(security_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing security files: {', '.join(missing_files)}")
        return False
    
    print("✅ Security files validation passed")
    return True

def validate_readme():
    """Validate README file"""
    print("🔍 Validating README file...")
    
    readme_path = os.path.join(MODULE_PATH, "README.md")
    if not os.path.exists(readme_path):
        print("❌ README.md file not found!")
        return False
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Check for essential sections
        required_sections = [
            "Overview", "Key Features", "Installation", "Configuration"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in readme_content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing README sections: {', '.join(missing_sections)}")
            return False
        
        print("✅ README validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Error validating README: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 KPI Tracking Module - Pre-Publication Validation")
    print("=" * 50)
    
    validations = [
        validate_manifest,
        validate_demo_data,
        validate_static_images,
        validate_license,
        validate_security,
        validate_readme
    ]
    
    passed = 0
    total = len(validations)
    
    for validation in validations:
        if validation():
            passed += 1
        print()
    
    print(f"📊 Validation Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 Module is ready for Odoo App Store publication!")
        print("📝 Next steps:")
        print("   1. Create and add static images")
        print("   2. Test installation in clean Odoo 18 instance")
        print("   3. Submit to Odoo App Store")
    else:
        print("⚠️ Module needs additional work before publication")
        print("   Please address the validation errors above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
