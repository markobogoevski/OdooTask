# Tech Gear Inventory Module

_The Tech Gear Inventory module is an Odoo add-on that simplifies and automates the process of managing product data for a tech inventory. The module is designed to handle bulk imports of products and categories from Excel files, validate data, and ensure accurate product information in the database. It also provides a user-friendly wizard for importing Excel files through the Odoo interface._
### Features

1. Excel Import Wizard:
    * Allows importing products and categories directly from an Excel file.
    * Provides batch processing with configurable chunk sizes to improve performance.
    * Validates data for required fields and correct data types, ensuring data integrity.
    * Includes detailed error logging with a downloadable error log file for user reference.

2. Optimizations:
    * Caching mechanism for categories to reduce redundant database queries.
    * Batch updates and creations of records, minimizing database writes.
    * Configurable chunk size to control the number of records processed in each batch, optimizing database load.

3. Data Validation:
    * Mandatory Fields: Ensures that essential fields like Product Name and Category are provided.
    * Data Types: Validates that Price and Quantity are numeric to prevent database errors.
    * Error Logging: Logs any errors found during validation and processing, with specific details such as row number and error type (e.g., missing field or incorrect data type).

4. UI Components:
    * Custom form and list views for Product Category and Product Template to facilitate product and category management. These override the parent views for Template and Category to only include relevant fields from the excel file.
    * A top-level menu for easy navigation, including options to manage categories, products, and initiate the Excel import wizard.
    * An Excel import wizard that provides an intuitive UI for file selection and initiates the import and validation process.
    * An Excel import error view that enables the user to navigate to a page where the error is logged.

### Module Structure

#### 1. Excel Import Wizard

The Excel Import Wizard allows users to upload an Excel file with product data and start the import process. The file is processed and validated row-by-row, ensuring all data is accurate before being saved in the database.
Key Components:
* File Upload: Users can upload an Excel file containing product data.
* Data Validation: Each row in the file is validated for required fields and data types. Errors are logged in a downloadable error log. 
* Batch Processing: Data is processed in configurable chunks to improve performance and reduce database load. 
* Error Log: If any errors occur during import, the wizard generates a detailed log with row-specific information (e.g., "Row 2: Invalid price 'ABC' - must be numeric").
#### 2. Views

Custom views are provided for managing Product Template and Product Category, as well as an import wizard view.

* Product Category View: The category view allows users to view existing categories. The description field in each category is customizable.
* Product Template View: This view shows products with details like Price, Quantity, and Category.
* Excel Import Wizard View: A form for uploading an Excel file and initiating the import process. Once an import is complete, users can download an error log file if any issues were encountered.
* Excel Import Error Log View: Enables the user to see the error logs if any were present during the import. 

#### 3. Models

* ProductTemplate Model: We extend the product.template to include a categ_id with ManyToOne relation, a price and a quantity field. Although these fields could be mapped to ones inherited directly from the product module, I saw it as ambiguous because of the naming convention and decided to just create my own fields.
* ProductCategory Model: In the specification, there is a suggestion to create a new model for this but there is no need to do this. The product module already exposes a product.category table which links to the product.template. We extend it by adding a description field. If we wanted to create a new model for this purpose we would need 
to implement this model in a way which would satisfy all field population requirements that the product.template relationship and product modules dictates with it.
#### 4. Helper Classes

* ProductData Class: Encapsulates individual row data from the Excel file and performs validation on each row.
* CategoryManager: Manages retrieval and creation of product categories. Implements a cache to minimize repeated database queries for the same category.
* ProductManager: Manages the retrieval and creation of products, processing them in batch mode to reduce database load.
* ExcelImportWizard: The actual wizard responsible for the whole flow of importing an excel file and reading the data into database

#### 5. Dependencies

* Product Module: The product module is required as it provides the base models product.template and product.category, which this module extends.
* Stock Module (Optional): This module may be included if advanced stock features are required for the products, but it is not mandatory for the core functionality.

### Optimizations

The module incorporates several optimizations to handle large datasets efficiently:

* Category Caching: Caches category instances to avoid redundant database queries, improving performance during large imports.
* Batch Processing: Processes records in batches (chunk size configurable, default is 100), reducing the number of database writes and optimizing the import flow.
* Error Handling and Logging: Errors are accumulated in a log, which can be downloaded, allowing users to review and fix issues without re-importing successful rows.

### Validation and Error Handling

Data validation is performed during import to ensure data integrity. The validation rules include:

* Mandatory Fields: Both Product Name and Category fields are required for each row.
* Data Types: Price and Quantity fields must be numeric. Errors like Row 2: Invalid price 'ABC' - must be numeric provide specific feedback to users.
* Error Log File: In case of any validation or processing errors, the wizard provides a downloadable error log, helping users quickly identify and correct issues.

### Installation

To install the Tech Gear Inventory module:
  * Clone or download the module into the Odoo addons folder.
  * Ensure all required dependencies (like product) are installed.
  * Update the Odoo Apps list and install the Tech Gear Inventory module from the Apps menu.

### Development notes and environment setup

When developing this custom module, I used a Windows OS with the latest Odoo 18 server installation. To avoid directly
modifying the Odoo python files I created a separate directory which is pushed to github and have added a symlink between the addons
folder in my directory and the addons folder inside odoo/server/addons official directory. This enables the Odoo server to look at both directories whenever it is 
registering its addons. The custom addons directory has also been added
to the .conf file in odoo alongside the original addons folder. This development setup has several pros in my opinion. First it prevents
the developer from changing already built in odoo modules which might reduce potential corruption and addon crashes in the future. Second it 
decouples the implementation of custom modules into a separate directory which can be version controlled and extended easily. Third, it allows 
for an isolated environment which will be built on top of the Odoo server's current python environment, meaning any new packages can be added in a separate 
requirements file. For the developer to be able to leverage Odoo's official modules and code, inside the content root setting of any IDE the Odoo 
official directory can be added (server). This enables imports in the form of: `from odoo import models, fields` with autocompletion and IDE support. To make sure that the same Python 
virtual environment is being used for running the official Odoo server and while developing custom addons, the interpreter needs to point to the python.exe file inside Odoo's directory.

### Usage

1. Navigate to Tech Gear Inventory > Import Product Data.

2. Upload an Excel file with the following header format:
- Product Name ; Category ;	Price ;	Quantity


3. Click Import to start the import process. If any errors are detected, an error log will be provided for download.

### Testing

Unit tests cover the following components:

* ProductData Class: Tests validation for product data, ensuring correct error handling.
* CategoryManager: Verifies retrieval and creation of categories with caching functionality.
* ProductManager: Tests batch creation and update of products, including error handling.
* ExcelImportWizard: End-to-end tests for the import process, validating data insertion, updating, and error handling.

To run the tests:


- Run Odoo's built-in test runner (Replace with Odoo's python interpreter, odoo-bin path and the database name, mine is odoo18)
`F:\OdooServer\python\python.exe F:\OdooServer\server\odoo-bin -d odoo18 -i tech_gear_inventory --test-enable --stop-after-init --log-level=test`

### Configuration Configurable Parameters

- Chunk Size for Batch Processing: Modify the batch size in the configuration to optimize performance for large imports.

In odoo.conf:

`[options]
tech_gear_inventory_chunk_size=100  # default value, adjust as necessary`

### Limitations and Considerations

* Error Handling: This module logs and skips rows with errors rather than halting the import, allowing for partial success and facilitating correction on re-import. This doesn't stop the import process, rather only skips invalid rows. Re-importing the file with the corrected rows will only add those and update the previous ones. It won't add duplicates nor corrupt the data.
* Concurrent Imports: Ensure that multiple users don’t import simultaneously to avoid conflicting updates.

### Github link
[Github link](https://github.com/markobogoevski/OdooTask/tree/master)

### Author

Developed by Marko Bogoevski, this module is designed for tech companies needing efficient inventory management with bulk data imports and error handling.