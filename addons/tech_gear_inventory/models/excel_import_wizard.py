# tech_gear_inventory/models/excel_import_wizard.py
import base64
from io import BytesIO
import openpyxl
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ProductData:
    """Encapsulates data and validation logic for a single row in the Excel file."""

    def __init__(self, product_name, category_name, price, quantity, row_index):
        self.product_name = product_name
        self.category_name = category_name
        self.price = price
        self.quantity = quantity
        self.row_index = row_index
        self.is_valid = True  # Track if the row is valid or not

    def validate(self, error_log):
        """
        Validate row data and log errors if necessary.
        This method updates the is_valid attribute based on validation outcome.
        """
        self.is_valid = True  # Start by assuming the row is valid

        if not self.product_name or not self.category_name:
            error_log.append(_("Row %d: Missing 'Product Name' or 'Category'.") % self.row_index)
            self.is_valid = False

        if not isinstance(self.price, (int, float)):
            error_log.append(_("Row %d: Invalid price '%s' - must be numeric.") % (self.row_index, self.price))
            self.is_valid = False

        if not isinstance(self.quantity, (int, float)):
            error_log.append(_("Row %d: Invalid quantity '%s' - must be numeric.") % (self.row_index, self.quantity))
            self.is_valid = False

        return self.is_valid


class CategoryManager:
    """Manages retrieval and creation of categories with caching for performance."""

    def __init__(self, env):
        self.env = env
        self.category_cache = {}  # Cache for categories to minimize DB queries

    def get_or_create(self, category_name, category_description):
        """
        Retrieve or create a product category based on its name.
        Updates the description if the category already exists.
        Uses a cache to reduce database queries for repeated categories in the same import.
        """
        # Check if the category is cached
        if category_name in self.category_cache:
            category = self.category_cache[category_name]
            # Update description if needed for cached category
            if category.description != category_description:
                category.write({'description': category_description})
            return category

        # Search for an existing category by name
        category = self.env['product.category'].search([('name', '=', category_name)], limit=1)
        if category:
            # Update the description if it's different
            if category.description != category_description:
                category.write({'description': category_description})
        else:
            # Create a new category with the given name and description
            category = self.env['product.category'].create({
                'name': category_name,
                'description': category_description
            })

        # Cache the result after any necessary updates
        self.category_cache[category_name] = category
        return category


class ProductManager:
    """Manages retrieval and creation of products."""

    def __init__(self, env):
        self.env = env

    def batch_update_or_create(self, products_data, category_manager, error_log, chunk_size=100):
        """
        Batch process products to either create or update them in bulk, reducing database writes.
        :param products_data: List of ProductData instances
        :param category_manager: Instance of CategoryManager for category handling
        :param chunk_size: Number of records to process in each batch
        """
        for i in range(0, len(products_data), chunk_size):
            batch = products_data[i:i + chunk_size]

            # Separate data into "to_update" and "to_create" based on existing records
            to_update = []
            to_create = []

            for product_data in batch:
                # Get or create the category with name and description (they are the same because of the example excel file)
                category = category_manager.get_or_create(product_data.category_name, product_data.category_name)

                # Check if the product already exists
                product = self.env['product.template'].search([
                    ('name', '=', product_data.product_name),
                    ('categ_id', '=', category.id)
                ], limit=1)

                # Prepare data for bulk operation
                product_data_dict = {
                    'name': product_data.product_name,
                    'categ_id': category.id,
                    'price': product_data.price,
                    'quantity': product_data.quantity
                }

                if product:
                    # Prepare for bulk update
                    to_update.append((product.id, product_data_dict))
                else:
                    # Prepare for bulk create
                    to_create.append(product_data_dict)

            # Perform bulk updates with error handling
            if to_update:
                for product_id, update_data in to_update:
                    try:
                        self.env['product.template'].browse(product_id).write(update_data)
                    except Exception as e:
                        # Log update error, but continue with the rest of the batch
                        error_log.append(_("Failed to update product '%s' in row %d: %s") % (
                            update_data['name'], product_data.row_index, str(e)
                        ))

            # Perform bulk creates with error handling
            if to_create:
                try:
                    self.env['product.template'].create(to_create)
                except Exception as e:
                    # Log creation error, and specify that these rows failed in bulk creation
                    error_log.append(_("Failed to create products in rows [%s]: %s") % (
                        ", ".join(str(data.row_index) for data in batch), str(e)
                    ))


class ExcelImportWizard(models.TransientModel):
    _name = 'tech.gear.excel.import.wizard'
    _description = 'Excel Import Wizard for Tech Gear Inventory'

    file = fields.Binary("File", required=True)
    error_log_file = fields.Binary("Error Log File", readonly=True, attachment=True)
    error_log_filename = fields.Char("Error Log Filename", readonly=True, default="error_log.txt")
    chunk_size = fields.Integer("Chunk Size", default=100, help="Number of records to process in each batch")

    def import_excel(self):
        # Load the sheet and initialize components
        sheet = self._load_excel_sheet()
        category_manager = CategoryManager(self.env)
        product_manager = ProductManager(self.env)

        # Initialize error log and valid row storage
        error_log = []
        valid_rows = []

        # Collect valid rows
        for row_index, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            product_data = ProductData(*row, row_index=row_index)
            if product_data.validate(error_log):
                valid_rows.append(product_data)

        # Process valid rows in batch and generate error log file if necessary
        product_manager.batch_update_or_create(valid_rows, category_manager, error_log, chunk_size=self.chunk_size)

        # If errors occurred, generate the error log file and open a dialog with a download button
        if error_log:
            self._generate_error_log_file(error_log)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'tech.gear.excel.import.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'name': _("Import Completed with Errors"),
                'view_id': self.env.ref(
                    "tech_gear_inventory.tech_gear_inventory_view_excel_import_wizard_error_dialog").id
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Import Successful"),
                    'message': _("The product data has been successfully imported."),
                    'sticky': False,
                }
            }

    def download_error_log(self):
        """
        Allows users to download the error log file after the import process if errors are present.
        """
        if self.error_log_file:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{self._name}/{self.id}/error_log_file/{self.error_log_filename}',
                'target': 'self',
            }
        else:
            raise ValidationError(_("No error log file available for download."))

    def _generate_error_log_file(self, error_log):
        log_content = "\n".join(error_log)
        log_file = BytesIO()
        log_file.write(log_content.encode('utf-8'))
        log_file.seek(0)
        self.error_log_file = base64.b64encode(log_file.read())
        log_file.close()

    def _load_excel_sheet(self):
        try:
            data = base64.b64decode(self.file)
            workbook = openpyxl.load_workbook(filename=BytesIO(data), data_only=True)
            return workbook.active
        except Exception as e:
            raise ValidationError(_("Unable to load the Excel file. Ensure it's a valid file. Error: %s") % str(e))

