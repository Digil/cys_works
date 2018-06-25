{
    'name': 'Link SO and PO',
    'version': '8.0.1.0',
    'author': 'Cybrosys',
    'category': 'Sale',
    'summary': 'Link sale order and purchase order',
    'description': "LINK SALES ORDER AND PURCHASE ORDER ",
    'depends': ['base', 'sale', 'purchase'],
    'data': ['views/link_so_po_view.xml', 'views/add_projects_view.xml','security/sales_person.xml',
             'views/sale_order_workflow.xml','security/ir.model.access.csv'],
    'installable': True,


}