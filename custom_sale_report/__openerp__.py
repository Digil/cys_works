{
    'name': 'Sales Custom Qweb',
    'version': '1.0',
    'category': 'Sales Management',
    'sequence': 14,
    'summary': 'Print customized qweb report',
    'description': 'Allows you to print html format pdf report for the sale order',
    'author': 'Digil',
    'depends': ['sale', 'report'],
    'data': ['custom_sale_report.xml',
             'report_custom_saleorder.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
}