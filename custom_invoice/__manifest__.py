# -*- coding: utf-8 -*-
{
    'name': "custom_invoice",

    'summary': """
        Separate invoice based on product category""",

    'description': """
        This module aims to create separate invoices based on the product category.
    """,

    'author': "Digil",
    'website': "http://www.google.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'invoice',
    'version': '10.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
         'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'licence': 'AGPL-3',
    'installable': True,
    'auto-install': False,
    'application': False,
}