#!/usr/bin/env python
"""
Run salary component generator for tenant schemas
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from payroll.sample_salary_component import SalaryComponentGenerator

# Run for kk_company tenant
print("Running salary component generator for kk_company tenant...")
gen = SalaryComponentGenerator(tenant_schema='kk_company')
gen.run()
