import logging
from playwright.sync_api import sync_playwright, TimeoutError, Error
import time

logging.basicConfig(level=logging.INFO)

def run(playwright):
    browser = playwright.chromium.launch(channel="msedge", headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Log the start of the script
    logging.info("Starting the script...")

    # Navigate to the chat page
    logging.info("Navigating to https://huggingface.co/chat/")
    page.goto("https://huggingface.co/chat/")

    # Wait for the page to load completely
    logging.info("Waiting for the page to load completely...")
    page.wait_for_load_state('networkidle')

    # Wait for the chat input field to be visible with a longer timeout
    logging.info("Waiting for the chat input field to be visible...")
    try:
        page.wait_for_selector('textarea[placeholder="Ask anything"]', timeout=60000)
    except TimeoutError:
        logging.error("Timeout while waiting for the chat input field. Retrying...")
        page.wait_for_selector('textarea[placeholder="Ask anything"]', timeout=60000)

    # Chat loop
    while True:
        # Prompt the user for input
        user_input = input("You: ")

        # Find the chat input field and enter the user's message
        logging.info("Finding the chat input field...")
        chat_input = page.query_selector('textarea[placeholder="Ask anything"]')
        logging.info("Typing '%s' into the chat input field...", user_input)
        chat_input.fill(user_input)

        # Submit the form using the correct selector
        logging.info("Submitting the form...")
        submit_button_selector = "#app > div.grid.h-full.w-screen.grid-cols-1.grid-rows-\\[auto\,1fr\\].overflow-hidden.text-smd.md\\:grid-cols-\\[280px\,1fr\\].transition-\\[300ms\\].\\[transition-property\\:grid-template-columns\\].dark\\:text-gray-300.md\\:grid-rows-\\[1fr\\] > div > div.dark\\:via-gray-80.pointer-events-none.absolute.inset-x-0.bottom-0.z-0.mx-auto.flex.w-full.max-w-3xl.flex-col.items-center.justify-center.bg-gradient-to-t.from-white.via-white\\/80.to-white\\/0.px-3\\.5.py-4.dark\\:border-gray-800.dark\\:from-gray-900.dark\\:to-gray-900\\/0.max-md\\:border-t.max-md\\:bg-white.max-md\\:dark\\:bg-gray-900.sm\\:px-5.md\\:py-8.xl\\:max-w-4xl.\\[\&\>\*\\]\\:pointer-events-auto > div > form > div > button"
        page.click(submit_button_selector)

        # Wait for the AI to finish thinking and the response to be visible
        logging.info("Waiting for the AI to finish thinking and the response to be visible...")
        response_selector = 'div[class="group relative -mb-4 flex items-start justify-start gap-4 pb-4 leading-relaxed"]:last-child div[class="relative min-h-[calc(2rem+theme(spacing[3.5])*2)] min-w-[60px] break-words rounded-2xl border border-gray-100 bg-gradient-to-br from-gray-50 px-5 py-3.5 text-gray-600 prose-pre:my-2 dark:border-gray-800 dark:from-gray-800/40 dark:text-gray-300"] p'
        try:
            page.wait_for_selector(response_selector, timeout=60000)
        except TimeoutError:
            logging.error("Timeout while waiting for the AI response. Retrying...")
            page.wait_for_selector(response_selector, timeout=60000)

        # Add a small delay to ensure the full response is generated
        time.sleep(6)  # Adjust the delay as needed

        # Validate the response selector
        if not page.query_selector(response_selector):
            logging.error(f"Selector validation failed: {response_selector}")
            continue

        # Capture the response
        logging.info("Capturing the response...")
        try:
            response = page.query_selector(response_selector).text_content()
            logging.info("AI Response: %s", response)
            print(f"Bot: {response}")
        except Error as e:
            logging.error("Error while capturing the response: %s", e)

    # Keep the browser open until force quit
    logging.info("Browser is open. Press Ctrl+C to close.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Closing browser...")
        browser.close()

with sync_playwright() as playwright:
    run(playwright)