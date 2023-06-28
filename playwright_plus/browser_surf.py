# Built-in imports
import logging
from random import randint

# Public 3rd party packages imports
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Page, Locator
from asyncio.exceptions import CancelledError

# Private packages imports
# Local functions and relative imports
# Constants imports
# New constants
EXCLUDED_RESOURCES_TYPES = ["stylesheet", "image", "font", "svg"]

__all__ = [
    "check_for_loaded_marker",
    "open_new_page",
    "wait_after_execution",
    "with_page",
]


def create_block_resources(resources_to_block: list):
    """Create a function that blocks specified resources.

    Args:
        resources_to_block (List[str]): List of the resources to block.

    Returns:
        callable: A function that can be used as a route handler to block resources.
    """
    def _block_resources(route):
        """
        See
        - https://playwright.dev/python/docs/api/class-request#request-resource-type
        - https://www.zenrows.com/blog/blocking-resources-in-playwright#blocking-resources

        Block specified resources

        Args:
            route (Route): The route object.
        Raises:
            CancelledError: If the resource type matches the ones to block, the route is aborted.

        Notes: This function check the `route.request.resource_type` to determine the type of resource. It compares with the `resources_to_block` list and
            aborts the route if there is a match. Otherwise, the route continues normally.
        """
        try:
            if route.request.resource_type in resources_to_block:
                route.abort()

            else:
                route.continue_()

        except CancelledError as err:
            logging.debug("block_resources was correctly canceled")

    return _block_resources


# WEB BROWSER AND PAGE OPENING


def _instantiate_browser_context_page(
    p,
    proxy_info: dict = None,
    headless: bool = True,
    accept_downloads: bool = True,
    block_resources: bool | list = True,
    cookies: list[dict] = None,
    browser_type: str = "chromium",
    **kwargs,
):
    """
    Instantiate a browser, browser context, and a new page with specified configurations

    Args:
        p: Playwright instance.
        proxy_info (dict, optional): Proxy information. Defaults to None.
        headless (bool, optional): Headless mode. Defaults to True.
        accept_downloads (bool, optional): Whether to accept downloads. Defaults to True.
        block_resources (bool | list, optional): Whether to block resources during page navigation.
            If True, it blocks the default resource types. If a list is provided, only the specified
            resource types are blocked. Defaults to True.
        cookies (list[dict], optional): List of cookies to set in the browser context. Defaults to None.
        browser_type (str, optional): The type of browser to launch. Defaults to "chromium".
        **kwargs: Additional keyword arguments for browser configuration.

    Returns:
        tuple: A tuple containing the browser, browser context, and new page.
    """
    # open chromium browser, using specified proxy
    logging.debug(
        f"[playwright_plus] open a browser : headless={headless}, proxy_info={proxy_info.get('server') if isinstance(proxy_info, dict) else None}"
    )
    match browser_type:
        case "chromium":
            browser = p.chromium.launch(headless=headless, proxy=proxy_info)
        case "firefox":
            browser = p.firefox.launch(headless=headless, proxy=proxy_info)
    # create the browser context
    logging.debug(
        f"[playwright_plus] open a browser context: accept_downloads={accept_downloads}, with {len(cookies) if cookies else 0} cookies set(s)"
    )
    context = browser.new_context(accept_downloads=accept_downloads)
    context.add_init_script(
        """
            navigator.webdriver = false
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            })
        """
    )
    if cookies:
        context.add_cookies(cookies)

    # open a web page
    logging.debug(
        f"[playwright_plus] open a new page: blocked resources={EXCLUDED_RESOURCES_TYPES if block_resources==True else block_resources}"
    )
    page = context.new_page()
    if block_resources:
        resources_to_block = (
            EXCLUDED_RESOURCES_TYPES if block_resources == True else block_resources
        )

        def _block_resources(route):
            try:
                if route.request.resource_type in resources_to_block:
                    route.abort()

                else:
                    route.continue_()

            except CancelledError as err:
                logging.debug("block_resources was correctly canceled")

        page.route("**/*", _block_resources)

    return browser, context, page


def open_new_page(
    proxy_info: dict = None,
    headless: bool = True,
    accept_downloads: bool = True,
    block_resources: bool | list = True,
    cookies: list[dict] = None,
    **kwargs,
):
    """Open a new browser, browser context, and page with specified configurations.

    Args:
        proxy_info (dict, optional): Proxy information. Defaults to None.
        headless (bool, optional): Headless mode. Defaults to True.
        accept_downloads (bool, optional): Whether to accept downloads. Defaults to True.
        block_resources (bool | list, optional): Whether to block resources during page navigation.
            If True, it blocks the default resource types. If a list is provided, only the specified
            resource types are blocked. Defaults to True.
        cookies (list[dict], optional): List of cookies to set in the browser context. Defaults to None.
        **kwargs: Additional keyword arguments for browser configuration.

    Returns:
        tuple: A tuple containing the browser, browser context, and new page.
    """
    p = sync_playwright().start()

    browser, context, page = _instantiate_browser_context_page(
        p,
        proxy_info=proxy_info,
        headless=headless,
        accept_downloads=accept_downloads,
        block_resources=block_resources,
        cookies=cookies,
    )

    return browser, context, page


def with_page(**kwargs):
    """Decorator to open a new page and it is the decorated function.

    Args:
        **kwargs: Keyword arguments to configure the browser, browser context, and page.

    Returns:
        callable: Decorator function.
    """
    def decorator(func):
        def func_wrapper(*func_args, **func_kwargs):
            # by default, accept_downloads=True, headless=True, block_resources=True, no proxy, no cookies
            default = {
                "accept_downloads": True,
                "headless": True,
                "block_resources": True,
                "proxy_info": None,
            }
            for k, v in default.items():
                if k not in kwargs:
                    kwargs[k] = v

            # overwrite the decorator kwargs if the ones specified by the wrapped function
            kwargs.update(func_kwargs)

            # open browser, context and page with the conditions specified in the kwargs dictionary
            with sync_playwright() as p:
                browser, context, page = _instantiate_browser_context_page(
                    p, **kwargs)

                # add the new page to the wrapped function kwargs
                func_kwargs["page"] = page

                # execute the function with the open page
                output = func(*func_args, **func_kwargs)

                # close the page and browser
                page.close()
                browser.close()

            return output

        return func_wrapper

    return decorator


# WEB SURFING
def _get_page_arg(func_args: list, func_kwargs: dict, func_name: str) -> Page:
    """Get the `Page` argument from the function's arguments or keyword arguments.

    Args:
        func_args (list): List of arguments of the function.
        func_kwargs (dict): The function's keyword arguments.
        func_name (str): The name of the function.

    Returns:
        Page: The `Page` object.

    Raises:
        Exception: If the `Page` object is not found in the function's arguments or keyword arguments.
    """
    page = None
    if func_kwargs:
        page = func_kwargs.get("page")
    if (not page) and func_args:
        page = func_args[0]
    if not isinstance(page, Page):
        raise Exception(
            f"One of the decorator expects the function `{func_name}` to have a page as first arg or as kwarg."
        )
    return page


def wait_after_execution(wait_ms: int = 2000, randomized: bool = True):
    """Decorator to add a delay after executing a function.

    Args:
        wait_ms (int, optional): The duration of the delay. Defaults to 2000.
        randomized (bool, optional): Whether to randomize the delay. Defaults to True.

    Returns:
        callable: Decorator function.
    """
    def decorator(func):
        def func_wrapper(*func_args, **func_kwargs):
            # get the page object. Check the kwargs first, then the first args
            page = _get_page_arg(func_args, func_kwargs, func.__name__)

            # execute the function
            output = func(*func_args, **func_kwargs)

            # wait for the given time before moving to the next command
            nonlocal wait_ms
            # the wait_ms value can be overwritten if it is specified as a kwarg in the wrapped function
            if func_kwargs and ("wait_ms" in func_kwargs):
                wait_ms = func_kwargs.get("wait_ms")

            if randomized:
                # take a random number in the 15% range around the input time in millisecond
                min = int(wait_ms * 0.85 + 0.5)
                max = int(wait_ms * 1.15 + 0.5)
                wait_ms = randint(min, max)
            # wait for the given time before moving to the next command
            page.wait_for_timeout(wait_ms)

            return output

        return func_wrapper

    return decorator


def check_for_loaded_marker(
    marker: str | Locator = None,
    marker_strict: bool = False,
    load_message: str = None,
    timeout: int = 10000,
):
    """Decorator to check for the marker loaded or not loaded.

    Args:
        marker (Union[str, Locator], optional): The marker to check for. Defaults to None.
        marker_strict (bool, optional): Whether the marker should match strictly. Defaults to False.
        load_message (str, optional): The message to log when the marker is visible. Defaults to None.
        timeout (int, optional): The timeout to wait for the marker to become visible. Defaults to 10000.

    Returns:
        callable: Decorator function.
    """
    def decorator(func):
        def func_wrapper(*func_args, **func_kwargs):
            # get the page object. Check the kwargs first, then the first args
            page = _get_page_arg(func_args, func_kwargs, func.__name__)

            # execute the function
            output = func(*func_args, **func_kwargs)

            # build the marker locator if needed
            nonlocal marker
            if isinstance(marker, str):
                # add a dot before the marker if it misses it
                if not (marker_strict) and not (marker.startswith(".")):
                    marker = "." + marker
                # make the marker a playwright Locator
                marker = page.locator(marker)
                # wait for the marker to be visible
                marker.wait_for(timeout=timeout)
                logging.debug(
                    load_message
                    if load_message
                    else "[playwright_plus] loaded marker visible."
                )

            return output

        return func_wrapper

    return decorator
