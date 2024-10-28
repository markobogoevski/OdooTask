You have been tasked with creating a custom Odoo module for a fictional company,
"Tech Gear Inc." This company sells a variety of electronic devices and accessories.
The module should streamline their inventory management by integrating existing
Odoo modules and incorporating functionality to parse product data from an Excel
file.
Requirements:
1. Module Creation:
• Create an Odoo module named tech_gear_inventory.
• Structure the module following Odoo's standard conventions.
2. Excel File Parsing:
• Implement functionality to parse an Excel file containing product data and
update the Odoo database accordingly.
• Ensure the module can handle a standard Excel file with the following
columns:
• Product Name
• Category
• Price
• Quantity
• Map these columns to existing fields in the product.template model.
3. Inventory Module Extension:
• Product Model:
• Extend the existing product.template model to include:
• category (Many2one): A relation to a product_category model.
• Implement a mechanism to synchronize data from the parsed Excel file
to the Odoo database.
• Product Category:
• Create a new product_category model with the following fields:
• name (Char): The name of the category.
• description (Text): A brief description of the category.

4. Views:
• Extend or create views to manage the models:
• Product Category Views:
• Create form, tree, and search views for managing the
product_category model.

5. Menus:
• Ensure the existing menus are extended or updated to navigate to each
model's views appropriately, and run the importer.

6. Functional Requirements
• Excel File Parsing: Ensure that the module correctly parses
an Excel file and updates the database accordingly.

7. Testing:
• Write a test to verify the functionality of the module:
• Excel Parsing: Ensure data from a sample Excel file is parsed correctly
and populates the database.

Submission:
1. Package the module into a zip file named tech_gear_inventory.zip.
2. Include a README file detailing the module's functionality, installation steps, and how
to use it.
3. Provide a sample Excel file named products_data.xlsx to demonstrate the parsing
functionality
Evaluation Criteria:
• Functionality: The module meets all the specified functional requirements.
• Code Quality: The code is clean, follows best practices, and is well-documented.
• UI/UX: The views are user-friendly and intuitive.
• Testing: Tests cover the primary functionalities and pass successfully.
