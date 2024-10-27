# tech_gear_inventory/models/product_category.py
from odoo import models, fields

class ProductCategory(models.Model):
    # We inherit from product.category instead of creating a new model, since Odoo stock module already provides this
    # relation. We extend the model to include the description field (name field is already present)

    _inherit = 'product.category'

    description = fields.Text(
        string="Description",
        help="Description of the category"
    )
