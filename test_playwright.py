import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    try:
        print("Starting Playwright...")
        playwright = await async_playwright().start()
        print("Playwright started successfully")
        
        print("Launching browser...")
        browser = await playwright.chromium.launch()
        print("Browser launched successfully")
        
        print("Creating context...")
        context = await browser.new_context()
        print("Context created successfully")
        
        await context.close()
        await browser.close()
        await playwright.stop()
        print("Playwright test completed successfully")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_playwright())