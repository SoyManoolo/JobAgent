from playwright.sync_api import sync_playwright


def crear_navegador(persistent=False):
    playwright = sync_playwright().start()

    if persistent:
        browser = None
        context = playwright.chromium.launch_persistent_context(
            user_data_dir="scraper/profile",
            headless=True,
        )

        page = context.new_page() if len(context.pages) == 0 else context.pages[0]

        return playwright, browser, context, page

    browser = playwright.chromium.launch(headless=False)

    context = browser.new_context()

    page = context.new_page()

    return playwright, browser, context, page
