# Python-Tests

### Project structure:
1. [root/core](https://github.com/vlad2102/Python-Tests/tree/main/root/core) - functions and classes that describe the basic functionality and which can be reused in subprojects
2. [root/site](https://github.com/vlad2102/Python-Tests/tree/main/root/site) - description of the tested project
    1. [./api](https://github.com/vlad2102/Python-Tests/tree/main/root/site/api) - classes for working with the project via api
    2. [./db](https://github.com/vlad2102/Python-Tests/tree/main/root/site/db) - ORM classes for using the project database
    3. [./page_objects](https://github.com/vlad2102/Python-Tests/tree/main/root/site/page_objects) - classes describing front structure of the project 
3. [root/tests](https://github.com/vlad2102/Python-Tests/tree/main/root/tests) - project tests

### Description of files in [root/core](https://github.com/vlad2102/Python-Tests/tree/main/root/core) folder
* base_api.py - base class for working with api
* base_elements.py - base class for interacting with web-elements on pages (in the page object pattern)
* base_page.py - base class for interacting with pages (in the page object pattern)
* browser.py - a factory class for initializing the browser and extending it with custom methods
* config.py - project configuration file
* helpers_db.py - functions for working with the database
* visual_functions.py - functions for taking and saving screenshots, including full-page screenshots

### Interesting in [root/site](https://github.com/vlad2102/Python-Tests/tree/main/root/site) folder
* db/tables.py - metadata of existing tables is used to make an ORM representation of an existing database
* page_objects/front/shop/cart_page.py - because of the low speed of parsing the page by selenium, the lxml module was used. lxml - module for building the html structure of pages from a string and getting information from them

### Description of files in [root/tests](https://github.com/vlad2102/Python-Tests/tree/main/root/tests) folder
* api/test_add_product.py - tests that interact with the project via api. Preparation and verification of tests is carried out in the database
* test_e2e.py - tests built on user stories (using the page object pattern)
* test_orders.py - tests are built on a test template. Test steps use api, test check is occur in browser on the page (using the page object pattern)
* test_visual.py - visual tests based on comparison of screenshots