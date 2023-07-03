# Unittest playwright_plus module

Custom unittest of the playwright_plus

## Requirements

To run the unit tests, you need the following dependencies installed:

- unittest:
- playwright

## Running the Tests

To run the unit tests, execute the following command in your terminal:

`python -m unittest <test_file_name>`

Replace `<test_file_name>` with the name of the file containing the unit tests.

## Test Cases

### test_create_block_resources

This test case verifies the functionality of the `create_block_resources` function.

1. Test with positive case:
   * Mock a route with resource type 'video'.
   * Call `block_resources` function with the mocked route.
   * Assert that `continue_` method of the route is called.
2. Test with negative case:
   * Mock a route with resource type 'image'.
   * Call `block_resources` function with the mocked route.
   * Assert that `abort` method of the route is called.

### test_open_new_page

This test case verifies the functionality of the `open_new_page` function.

1. Mock the `playwright.sync_api.sync_playwright` method.
2. Set up mock objects for the `launch`, `new_context`, and `new_page` methods.
3. Call the `open_new_page` function.
4. Assert the following:
   * `playwright.sync_api.sync_playwright` method is called.
   * `launch` method is called with the correct parameters.
   * `new_context` method is called.
   * `add_init_script` method is called.
   * `add_cookies` method is not called.
   * `new_page` method is called.
   * The returned `page` object is the same as the mock page object.
5. Verify the cleanup operations:
   * `stop` method of the playwright object is called.
   * `close` method of the browser object is called.
   * `close` method of the context object is called.

### test_with_page

This test case verifies the functionality of the `with_page` decorator.

1. Mock the `playwright.sync_api.sync_playwright` method.
2. Set up mock objects for the `launch`, `new_context`, and `new_page` methods.
3. Define a test function decorated with `with_page`.
4. Call the test function.
5. Assert the following:
   * `playwright.sync_api.sync_playwright` method is called.
   * `launch` method is called with the correct parameters.
   * `new_context` method is called.
   * `add_init_script` method is called.
   * `add_cookies` method is not called.
   * `new_page` method is called.
   * The returned result is the same as the mock page object.
6. Verify the cleanup operations:
   * `stop` method of the playwright object is called.
   * `close` method of the browser object is called.
   * `close` method of the context object is called.

### test_wait_after_execution

This test case verifies the functionality of the `wait_after_execution` decorator.

1. Define a mock `Page` class with a `wait_for_timeout` method.
2. Define a test function decorated with `wait_after_execution`.
3. Create an instance of the mock `Page` class.
4. Call the test function with the mock page object.
5. Assert the following:
   * The returned result is "result".
   * The `wait_for_timeout` method of the page object is called.
   * The timeout parameter passed to `wait_for_timeout` is

### test_set_json_to_page
This test case verifies the functionality of the set_json_to_page function.

1. Create a Page object.
2. Create a buffer containing JSON data.
3. Call the set_json_to_page function with the Page object and the buffer.
4. Assert that the target_json attribute of the Page object is equal to the buffer.
### test_construct_handle_response
This test case verifies the functionality of the construct_handle_response function.

1. Create a Page object.
2. Define the json_url_subpart.
3. Call the construct_handle_response function with the Page object and the json_url_subpart.
4. Create a mock response object with a URL matching the json_url_subpart.
5. Patch the set_json_to_page function and assert that it is called with the Page object and the response's JSON data.
6. Call the handle_response function with the mock response object.
### test_intercept_json_playwright
This test case verifies the functionality of the intercept_json_playwright function.

1. Call the intercept_json_playwright function with the provided parameters.
2. Assert that the returned result is an instance of a dictionary.