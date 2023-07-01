import unittest
from unittest.mock import patch
from playwright.sync_api import Page
from web_intercept import (
    set_json_to_page,
    construct_handle_response,
    intercept_json_playwright
)

class TestYourModule(unittest.TestCase):
    def setUp(self):
        self.page_url = "https://example.com"
        self.json_url_subpart = "/api/data"

    def test_set_json_to_page(self):
        page = Page()
        buffer = {"data": {"name": "Duy", "age": 26}}
        set_json_to_page(page, buffer)
        self.assertEqual(page.target_json, buffer)

    def test_construct_handle_response(self):
        page = Page()
        json_url_subpart = "/api/data"
        handle_response = construct_handle_response(page, json_url_subpart)
        response = type("MockResponse", (), {"url": "https://example.com/api/data"})
        with patch("web_intercept.set_json_to_page") as mock_set_json_to_page:
            handle_response(response)
            mock_set_json_to_page.assert_called_with(page, response.json())

    def test_intercept_json_playwright(self):
        result = intercept_json_playwright(
            self.page_url,
            self.json_url_subpart,
            timeout=2000,
            max_refresh=2,
        )
        self.assertIsInstance(result, dict)