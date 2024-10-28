# tech_gear_inventory/__manifest__.py
{
    'name': 'Tech Gear Inventory',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Custom inventory management for Tech Gear Inc.',
    'description': """
        Tech Gear Inventory module provides an inventory management system for
        managing product categories and importing product data from Excel files.
    """,
    'author': 'Marko Bogoevski',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/excel_import_wizard_view.xml',
        'views/excel_import_wizard_error_dialog.xml',
        'views/product_category_view.xml',
        'views/product_template_view.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True
}
