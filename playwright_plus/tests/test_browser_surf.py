import unittest
from unittest.mock import patch, MagicMock
from playwright.sync_api import Page
from browser_surf import (
	open_new_page,
	with_page,
	wait_after_execution,
	check_for_loaded_marker,
	create_block_resources
)


class TestCodeModule(unittest.TestCase):
	def test_create_block_resources(self):
		resources_to_block = ['image', 'font']
		block_resources = create_block_resources(resources_to_block)

		# test with positive case
		mock_route = MagicMock()
		mock_route.continue_ = MagicMock()
		mock_route.request.resource_type = 'video'
		block_resources(mock_route)
		mock_route.continue_.assert_called_with()

		# test with negative case
		mock_route = MagicMock()
		mock_route.abort = MagicMock()
		mock_route.request.resource_type = 'image'		
		block_resources(mock_route)
		mock_route.abort.assert_called_with()	

	def test_open_new_page(self, mock_playwright):
		# Mock the sync_playwright method
		mock_p = mock_playwright().start()
		mock_chromium = mock_p.chromium
		mock_browser = mock_chromium.launch.return_value
		mock_context = mock_browser.new_context.return_value
		mock_page = mock_context.new_page.return_value

		# Call the function
		browser, context, page = open_new_page()

		# Assertions
		mock_playwright.assert_called_once_with()
		mock_chromium.launch.assert_called_once_with(headless=True, proxy=None)
		mock_browser.new_context.assert_called_once_with(accept_downloads=True)
		mock_context.add_init_script.assert_called_once()
		mock_context.add_cookies.assert_not_called()
		mock_context.new_page.assert_called_once_with()
		mock_page.route.assert_called_once()
		self.assertEqual(page, mock_page)

		# Cleanup
		mock_p.stop.assert_called_once()
		mock_browser.close.assert_called_once()
		mock_context.close.assert_called_once()

	def test_with_page(self, mock_playwright):
		# Mock the sync_playwright method
		mock_p = mock_playwright().start()
		mock_chromium = mock_p.chromium
		mock_browser = mock_chromium.launch.return_value
		mock_context = mock_browser.new_context.return_value
		mock_page = mock_context.new_page.return_value

		# Define a test function
		@with_page()
		def test_function(page: Page):
			return page

		# Call the function
		result = test_function()

		# Assertions
		mock_playwright.assert_called_once_with()
		mock_chromium.launch.assert_called_once_with(headless=True, proxy=None)
		mock_browser.new_context.assert_called_once_with(accept_downloads=True)
		mock_context.add_init_script.assert_called_once()
		mock_context.add_cookies.assert_not_called()
		mock_context.new_page.assert_called_once_with()
		self.assertEqual(result, mock_page)

		# Cleanup
		mock_p.stop.assert_called_once()
		mock_browser.close.assert_called_once()
		mock_context.close.assert_called_once()

	def test_wait_after_execution(self):
		# Create a mock Page object
		class MockPage:
			def __init__(self):
				self.wait_for_timeout_called = False

			def wait_for_timeout(self, timeout):
				self.wait_for_timeout_called = True
				self.assertEqual(timeout, 2000)

		# Define a test function
		@wait_after_execution(wait_ms=2000)
		def test_function(page: Page):
			return "result"

		# Call the function
		page = MockPage()
		result = test_function(page)

		# Assertions
		self.assertEqual(result, "result")
		self.assertTrue(page.wait_for_timeout_called)

	def test_check_for_loaded_marker(self):
		# Create a mock Page object
		class MockPage:
			def __init__(self):
				self.wait_for_called = False

			def wait_for(self, marker, timeout):
				self.wait_for_called = True
				self.assertEqual(marker, ".marker")
				self.assertEqual(timeout, 10000)

		# Define a test function
		@check_for_loaded_marker(marker=".marker", timeout=10000)
		def test_function(page: Page):
			return "result"

		# Call the function
		page = MockPage()
		result = test_function
