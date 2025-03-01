"""
interpreter_smol vision browser - Web browser automation with visual capabilities
Adapted from smolagents/vision_web_browser.py
"""

import os
from io import BytesIO
from time import sleep
import tempfile

import helium
from dotenv import load_dotenv
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from smolagents import CodeAgent, tool
from smolagents.default_tools import DuckDuckGoSearchTool

# Default prompt messages
DEFAULT_PROMPT = """
I'm trying to find information on a topic. Please navigate to a relevant website and help me explore it.
"""

BROWSER_INSTRUCTIONS = """
Use your web_search tool when you want to get search results.
Then you can use helium to access websites. Don't use helium for search, only for navigating websites!
Don't bother about the helium driver, it's already managed.
We've already ran "from helium import *"
Then you can go to pages!

Code:
```py
go_to('github.com/trending')
```

You can directly click clickable elements by inputting the text that appears on them.
Code:
```py
click("Top products")
```

If it's a link:
Code:
```py
click(Link("Top products"))
```

If you try to interact with an element and it's not found, you'll get a LookupError.
In general stop your action after each button click to see what happens on your screenshot.
Never try to login in a page.

To scroll up or down, use scroll_down or scroll_up with as an argument the number of pixels to scroll from.
Code:
```py
scroll_down(num_pixels=1200) # This will scroll one viewport down
```

When you have pop-ups with a cross icon to close, don't try to click the close icon by finding its element or targeting an 'X' element (this most often fails).
Just use your built-in tool `close_popups` to close them:
Code:
```py
close_popups()
```

You can use .exists() to check for the existence of an element. For example:
Code:
```py
if Text('Accept cookies?').exists():
    click('I accept')
```

Proceed in several steps rather than trying to solve the task in one shot.
And at the end, only when you have your answer, return your final answer.
Code:
```py
final_answer("YOUR_ANSWER_HERE")
```

If pages seem stuck on loading, you might have to wait, for instance `import time` and run `time.sleep(5.0)`. But don't overuse this!
To list elements on page, DO NOT try code-based element searches like 'contributors = find_all(S("ol > li"))': just look at the latest screenshot you have and read it visually, or use your tool search_item_ctrl_f.
Of course, you can act on buttons like a user would do when navigating.
After each code blob you write, you will be automatically provided with an updated screenshot of the browser and the current browser url.
But beware that the screenshot will only be taken at the end of the whole action, it won't see intermediate states.
Don't kill the browser.
When you have modals or cookie banners on screen, you should get rid of them before you can click anything else.
"""


@tool
def search_item_ctrl_f(text: str, nth_result: int = 1) -> str:
    """
    Searches for text on the current page via Ctrl + F and jumps to the nth occurrence.
    Args:
        text: The text to search for
        nth_result: Which occurrence to jump to (default: 1)
    """
    driver = helium.get_driver()
    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
    if nth_result > len(elements):
        raise Exception(f"Match n°{nth_result} not found (only {len(elements)} matches found)")
    result = f"Found {len(elements)} matches for '{text}'."
    elem = elements[nth_result - 1]
    driver.execute_script("arguments[0].scrollIntoView(true);", elem)
    result += f"Focused on element {nth_result} of {len(elements)}"
    return result


@tool
def go_back() -> None:
    """Goes back to previous page."""
    driver = helium.get_driver()
    driver.back()


@tool
def close_popups() -> str:
    """
    Closes any visible modal or pop-up on the page. Use this to dismiss pop-up windows! This does not work on cookie consent banners.
    """
    driver = helium.get_driver()
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    return "Attempted to close popups by sending ESC key"


def save_screenshot(memory_step, agent):
    """Save a screenshot of the current browser state."""
    sleep(1.0)  # Let JavaScript animations happen before taking the screenshot
    driver = helium.get_driver()
    current_step = memory_step.step_number
    if driver is not None:
        for previous_memory_step in agent.memory.steps:  # Remove previous screenshots from logs for lean processing
            if hasattr(previous_memory_step, 'step_number') and previous_memory_step.step_number <= current_step - 2:
                previous_memory_step.observations_images = None
        png_bytes = driver.get_screenshot_as_png()
        image = Image.open(BytesIO(png_bytes))
        print(f"Captured a browser screenshot: {image.size} pixels")
        # Save to temporary file to ensure it persists
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image.save(temp_file.name)
        memory_step.observations_images = [temp_file.name]

    # Update observations with current URL
    url_info = f"Current url: {driver.current_url}"
    memory_step.observations = (
        url_info if memory_step.observations is None else memory_step.observations + "\n" + url_info
    )
    return


def initialize_driver():
    """Initialize the Selenium WebDriver."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument("--window-size=1000,1350")
    chrome_options.add_argument("--disable-pdf-viewer")
    chrome_options.add_argument("--window-position=0,0")
    return helium.start_chrome(headless=False, options=chrome_options)


def initialize_agent(model):
    """Initialize the CodeAgent with the specified model."""
    return CodeAgent(
        tools=[DuckDuckGoSearchTool(), go_back, close_popups, search_item_ctrl_f],
        model=model,
        additional_authorized_imports=["helium", "time", "os", "sys", "re", "urllib"],
        step_callbacks=[save_screenshot],
        max_steps=20,
        verbosity_level=2,
    )


def run_browser_session(prompt=None, model=None):
    """Run a browser session with the specified prompt and model."""
    if prompt is None:
        prompt = DEFAULT_PROMPT
    
    # Initialize the driver
    driver = initialize_driver()
    
    # Initialize and run the agent
    agent = initialize_agent(model)
    
    try:
        # Inject helium into the agent's namespace
        agent.python_executor("from helium import *", agent.state)
        
        # Run the agent with the prompt and browser instructions
        agent.run(prompt + "\n\n" + BROWSER_INSTRUCTIONS)
    except Exception as e:
        print(f"Error during browser session: {e}")
    finally:
        # Ask to close browser
        user_input = input("\nBrowser session completed. Close browser? (y/n) [y]: ")
        if user_input.lower() not in ['n', 'no']:
            try:
                helium.kill_browser()
                print("Browser closed.")
            except:
                print("Failed to close browser automatically. Please close it manually.")


# Command-line entry point
if __name__ == "__main__":
    load_dotenv()
    
    # Simple argument parsing
    import argparse
    parser = argparse.ArgumentParser(description="Run a web browser automation script")
    parser.add_argument("prompt", nargs="?", default=DEFAULT_PROMPT, help="The prompt to run")
    parser.add_argument("--model-type", type=str, default="gemini", 
                      choices=["gemini", "openai", "anthropic", "hf"],
                      help="Model type (gemini, openai, anthropic, hf)")
    parser.add_argument("--model-id", type=str, default=None,
                      help="Specific model ID")
    parser.add_argument("--api-key", type=str, default=None,
                      help="API key for the model provider")
    
    args = parser.parse_args()
    
    # Set environment variables
    if args.api_key:
        if args.model_type.lower() == "gemini":
            os.environ["GOOGLE_API_KEY"] = args.api_key
        elif args.model_type.lower() == "openai":
            os.environ["OPENAI_API_KEY"] = args.api_key
        elif args.model_type.lower() == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = args.api_key
        elif args.model_type.lower() == "hf":
            os.environ["HF_API_TOKEN"] = args.api_key
    
    # Create model
    if args.model_type.lower() == "gemini":
        from smolagents import LiteLLMModel
        model = LiteLLMModel(
            model_id=args.model_id or "gemini/gemini-2.0-flash",
            api_key=os.environ.get("GOOGLE_API_KEY"),
        )
    elif args.model_type.lower() == "openai":
        from smolagents import LiteLLMModel
        model = LiteLLMModel(
            model_id=args.model_id or "gpt-4o",
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
    elif args.model_type.lower() == "anthropic":
        from smolagents import LiteLLMModel
        model = LiteLLMModel(
            model_id=args.model_id or "claude-3-7-sonnet-latest",
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
    elif args.model_type.lower() == "hf":
        from smolagents import HfApiModel
        model = HfApiModel(
            model_id=args.model_id or "mistralai/Mistral-7B-Instruct-v0.2",
            token=os.environ.get("HF_API_TOKEN"),
        )
    
    # Run the browser session
    run_browser_session(prompt=args.prompt, model=model)