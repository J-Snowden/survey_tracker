import asyncio
import logging
from web_automation import WebAutomationModule

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_web_automation():
    try:
        print("Creating WebAutomationModule...")
        web_module = WebAutomationModule("test_downloads")
        
        print("Initializing WebAutomationModule...")
        web_initialized = await web_module.initialize()
        print(f"Initialization result: {web_initialized}")
        
        if web_initialized:
            print("Web automation module initialized successfully")
        else:
            print("Failed to initialize web automation module")
            
        # Try to close even if initialization failed
        print("Closing WebAutomationModule...")
        await web_module.close()
        print("WebAutomationModule closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Running detailed test...")
    asyncio.run(test_web_automation())
    print("Test completed")