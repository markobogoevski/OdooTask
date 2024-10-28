import base64
import re
from io import BytesIO
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
from odoo.addons.tech_gear_inventory.models.excel_import_wizard import ProductData, CategoryManager, ProductManager

class TestExcelImport(TransactionCase):
    def setUp(self):
        """Set up necessary test data."""
        super(TestExcelImport, self).setUp()
        # Sample test file
        self.test_file_path = 'F:/odoo_task/tech_gear/addons/tech_gear_inventory/tests/test_data.xlsx'
        self.category_manager = CategoryManager(self.env)
        self.product_manager = ProductManager(self.env)

    def test_product_data_validation(self):
        """Test the validation logic of ProductData class."""
        valid_product_data = ProductData("Valid Product", "Valid Category", 100.0,
                                         10, 2)
        invalid_product_data_price = ProductData("Invalid Product", "Invalid Category",
                                                 "ABC", 10, 3)
        invalid_product_data_quantity = ProductData("Another Invalid Product",
                                                    "Another Invalid Category", 100.0, "XYZ",
                                                    4)
        missing_data = ProductData(None, "Missing Category",
                                   50.0, 5, 5)

        # Set up error log
        error_log = []

        # Check that valid product data passes validation
        self.assertTrue(valid_product_data.validate(error_log), "Expected product data to be valid.")

        # Check that invalid product data with non-numeric price fails validation
        self.assertFalse(invalid_product_data_price.validate(error_log),
                         "Expected product data with non-numeric price to be invalid.")
        self.assertIn("Row 3: Invalid price 'ABC' - must be numeric.", error_log[-1])

        # Check that invalid product data with non-numeric quantity fails validation
        self.assertFalse(invalid_product_data_quantity.validate(error_log),
                         "Expected product data with non-numeric quantity to be invalid.")
        self.assertIn("Row 4: Invalid quantity 'XYZ' - must be numeric.", error_log[-1])

        # Check that missing data fails validation
        self.assertFalse(missing_data.validate(error_log), "Expected product data with "
                                                           "missing name to be invalid.")
        self.assertIn("Row 5: Missing 'Product Name' or 'Category'.", error_log[-1])

    def test_category_manager_get_or_create(self):
        """Test the get_or_create method of CategoryManager with caching and description updates."""
        # Create category initially
        category = self.category_manager.get_or_create("Update Category", "Initial Description")
        self.assertEqual(category.description, "Initial Description",
                         "Category description should match initial input.")

        # Update description
        updated_category = self.category_manager.get_or_create("Update Category", "Updated Description")
        self.assertEqual(updated_category.description, "Updated Description", "Category description should update.")

        # Check cache for consistency
        cached_category = self.category_manager.get_or_create("Update Category", "Updated Description")
        self.assertEqual(updated_category.id, cached_category.id, "Expected cached category ID to match updated ID.")

    def test_product_manager_batch_update_or_create(self):
        """Test the batch_update_or_create method of ProductManager with chunked batch processing."""
        # Prepare sample product data
        product_data_1 = ProductData("Product A", "Category A",
                                     100.0, 5, 2)
        product_data_2 = ProductData("Product B", "Category B",
                                     50.0, 10, 3)

        error_log = []

        # Run batch update or create
        self.product_manager.batch_update_or_create([product_data_1, product_data_2],
                                                    self.category_manager, error_log, chunk_size=1)

        # Check if products were created
        product_a = self.env['product.template'].search([('name', '=', 'Product A')])
        product_b = self.env['product.template'].search([('name', '=', 'Product B')])

        self.assertTrue(product_a, "Product A was not created.")
        self.assertEqual(product_a.price, 100.0, "Product A price mismatch.")
        self.assertEqual(product_a.quantity, 5, "Product A quantity mismatch.")

        self.assertTrue(product_b, "Product B was not created.")
        self.assertEqual(product_b.price, 50.0, "Product B price mismatch.")
        self.assertEqual(product_b.quantity, 10, "Product B quantity mismatch.")

        # Verify no errors
        self.assertFalse(error_log, f"Unexpected errors found: {error_log}")

    import re

    def test_excel_import(self):
        """Test the entire import workflow in ExcelImportWizard with valid and invalid data."""
        # Read and encode test file
        with open(self.test_file_path, 'rb') as file:
            encoded_file = base64.b64encode(file.read())

        # Create a wizard instance with the file
        wizard = self.env['tech.gear.excel.import.wizard'].create({
            'file': encoded_file,
            'chunk_size': 2  # Custom chunk size for testing
        })

        # Run import and check for both valid and invalid data
        try:
            wizard.import_excel()
        except ValidationError as e:
            error_log_file = BytesIO(base64.b64decode(wizard.error_log_file))
            error_log_content = error_log_file.read().decode('utf-8')
            self.fail(f"Import failed with ValidationError: {str(e)}\nError Log:\n{error_log_content}")

        # Check if products were created for valid data rows
        product_a = self.env['product.template'].search([('name', '=', 'Sample Product A')])
        product_b = self.env['product.template'].search([('name', '=', 'Sample Product B')])

        self.assertTrue(product_a, "Sample Product A import failed.")
        self.assertTrue(product_b, "Sample Product B import failed.")

        # Verify error logging for invalid rows dynamically
        if wizard.error_log_file:
            error_log_file = BytesIO(base64.b64decode(wizard.error_log_file))
            error_log_content = error_log_file.read().decode('utf-8')

            # Define patterns to look for specific error types
            price_error_pattern = re.compile(r"Row \d+: Invalid price '.*' - must be numeric.")
            missing_data_pattern = re.compile(r"Row \d+: Missing 'Product Name' or 'Category'.")

            # Assert patterns exist in the log content
            self.assertRegex(error_log_content, price_error_pattern, "Price error log entry missing.")
            self.assertRegex(error_log_content, missing_data_pattern, "Missing data error log entry missing.")

    def test_error_logging(self):
        """Test error logging functionality in import_excel method."""
        # Prepare invalid data to trigger errors
        invalid_data = ProductData("Invalid Product", "Invalid Category",
                                   "ABC", "XYZ", 6)
        valid_data = ProductData("Valid Product", "Valid Category",
                                 100.0, 10, 7)

        # Create an error log and pass both valid and invalid data
        error_log = []
        invalid_data.validate(error_log)
        valid_data.validate(error_log)

        # Verify error log contents
        self.assertIn("Row 6: Invalid price 'ABC' - must be numeric.", error_log)
        self.assertIn("Row 6: Invalid quantity 'XYZ' - must be numeric.", error_log)

    def test_generate_error_log_file(self):
        """Test that the error log file is generated correctly with import errors."""
        error_log = [
            "Row 3: Invalid price 'ABC' - must be numeric.",
            "Row 4: Missing 'Product Name' or 'Category'."
        ]

        # Create wizard instance and generate error log file
        wizard = self.env['tech.gear.excel.import.wizard'].create({})
        wizard._generate_error_log_file(error_log)

        # Decode and read the log file contents
        log_file_content = base64.b64decode(wizard.error_log_file).decode('utf-8')
        self.assertIn("Row 3: Invalid price 'ABC' - must be numeric.", log_file_content)
        self.assertIn("Row 4: Missing 'Product Name' or 'Category'.", log_file_content)
