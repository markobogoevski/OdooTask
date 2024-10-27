# tech_gear_inventory/models/product_template.py
from odoo import models, fields

class ProductTemplate(models.Model):
    # Here we inherit from product.template model. For the field mapping:
    # Product name can be mapped to "name" field in base model
    # We add price and quantity and override the categ_id to be many2one relation

    _inherit = 'product.template'

    categ_id = fields.Many2one(
        'product.category',
        string="Category",
        required=True,
        help="Select category for the product"
    )
    price = fields.Float(
        string="Price",
        help="The price of the product"
    )
    quantity = fields.Integer(
        string="Quantity",
        help="Quantity of the product"
    )
